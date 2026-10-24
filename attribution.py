"""Deterministic transaction attribution for the Mercy Ledger demo.

This module implements the project's explicit demo assumptions. It is not a
legal decision engine and does not establish ownership of funds beyond the
provided statement and complaint records.
"""
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, getcontext
import re

getcontext().prec = 40

CENT = Decimal("0.01")
SIX_PLACES = Decimal("0.000001")
_MONEY_RE = re.compile(r"^\d+\.\d{2}$")

ASSUMPTIONS = [
    "Debits consume tainted (disputed) money first, then clean money (taint-first). The SOP does not state a rule; both Annexure-V illustrations are consistent with it.",
    "If a debit hits one victim's money only, attribution is DIRECT. If it hits two or more victims' money together, it is split PRO-RATA to what each still has in the account (SOP Para 5(xiii)(b)).",
    "Provisional holds follow complaint order and the available balance (as printed in the Annexure-V Action Summary); restoration follows attribution. They can differ.",
]


def _parse_money(value, label):
    """Parse a contract-compliant money string without binary floats."""
    if not isinstance(value, str) or not _MONEY_RE.fullmatch(value):
        raise ValueError("%s must be a money string with exactly two decimals" % label)
    amount = Decimal(value)
    if amount < 0:
        raise ValueError("%s cannot be negative" % label)
    return amount


def _parse_timestamp(value, label):
    if not isinstance(value, str):
        raise ValueError("%s must be an ISO timestamp string" % label)
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("%s is not a valid ISO timestamp" % label) from exc
    if parsed.tzinfo is not None and parsed.utcoffset() is not None:
        raise ValueError("%s must not include a timezone; use the shared contract's local ISO format" % label)
    return parsed


def _money(value):
    return format(value.quantize(CENT, rounding=ROUND_HALF_UP), ".2f")


def _ratio(value):
    return format(value.quantize(SIX_PLACES, rounding=ROUND_HALF_UP), ".6f")


def _validate_case(case):
    if not isinstance(case, dict):
        raise ValueError("case must be a dictionary")
    required = [
        "case_id", "opening_balance", "transactions", "complaints",
        "seizure_timestamp",
    ]
    missing = [key for key in required if key not in case]
    if missing:
        raise ValueError("case is missing required keys: %s" % ", ".join(missing))

    opening = _parse_money(case["opening_balance"], "opening_balance")
    if not isinstance(case["transactions"], list):
        raise ValueError("transactions must be a list")
    if not isinstance(case["complaints"], list):
        raise ValueError("complaints must be a list")

    complaint_ids = set()
    complaint_by_utr = {}
    complaint_times = {}
    for index, complaint in enumerate(case["complaints"]):
        for key in ("complaint_id", "victim_label", "disputed_utr", "disputed_amount", "complaint_timestamp"):
            if key not in complaint:
                raise ValueError("complaint %d is missing %s" % (index + 1, key))
        complaint_id = complaint["complaint_id"]
        if complaint_id in complaint_ids:
            raise ValueError("duplicate complaint_id: %s" % complaint_id)
        complaint_ids.add(complaint_id)
        disputed = _parse_money(complaint["disputed_amount"], "complaint %s disputed_amount" % complaint_id)
        if disputed <= 0:
            raise ValueError("complaint %s disputed_amount must be positive" % complaint_id)
        utr = complaint["disputed_utr"]
        if utr in complaint_by_utr:
            raise ValueError("multiple complaints use disputed UTR %s; attribution is ambiguous" % utr)
        complaint_by_utr[utr] = complaint
        complaint_times[complaint_id] = _parse_timestamp(
            complaint["complaint_timestamp"], "complaint %s complaint_timestamp" % complaint_id
        )

    parsed_transactions = []
    txn_ids = set()
    credit_by_utr = {}
    for index, transaction in enumerate(case["transactions"]):
        for key in ("txn_id", "timestamp", "type", "amount", "utr", "narration"):
            if key not in transaction:
                raise ValueError("transaction %d is missing %s" % (index + 1, key))
        txn_id = transaction["txn_id"]
        if txn_id in txn_ids:
            raise ValueError("duplicate txn_id: %s" % txn_id)
        txn_ids.add(txn_id)
        txn_type = transaction["type"]
        if txn_type not in ("CREDIT", "DEBIT"):
            raise ValueError("transaction %s type must be CREDIT or DEBIT" % txn_id)
        amount = _parse_money(transaction["amount"], "transaction %s amount" % txn_id)
        if amount <= 0:
            raise ValueError("transaction %s amount must be positive" % txn_id)
        timestamp = _parse_timestamp(transaction["timestamp"], "transaction %s timestamp" % txn_id)
        parsed_transactions.append((timestamp, index, transaction, amount))
        if txn_type == "CREDIT":
            credit_by_utr.setdefault(transaction["utr"], []).append((timestamp, transaction, amount))

    for utr, complaint in complaint_by_utr.items():
        matches = credit_by_utr.get(utr, [])
        if len(matches) != 1:
            raise ValueError("complaint %s UTR %s must match exactly one CREDIT" % (complaint["complaint_id"], utr))
        credit_time, credit_tx, credit_amount = matches[0]
        disputed = _parse_money(complaint["disputed_amount"], "complaint disputed_amount")
        if credit_amount < disputed:
            raise ValueError("complaint %s disputed amount exceeds its matching credit" % complaint["complaint_id"])
        if complaint_times[complaint["complaint_id"]] <= credit_time:
            raise ValueError("complaint %s timestamp must follow its matching credit" % complaint["complaint_id"])

    seizure_value = case["seizure_timestamp"]
    seizure_time = None if seizure_value is None else _parse_timestamp(seizure_value, "seizure_timestamp")
    # Stable sort: when timestamps tie, the source row order is retained.
    parsed_transactions.sort(key=lambda row: (row[0], row[1]))

    # Validate that the full account ledger never goes negative.
    test_balance = opening
    for timestamp, _, transaction, amount in parsed_transactions:
        if transaction["type"] == "CREDIT":
            test_balance += amount
        else:
            test_balance -= amount
            if test_balance < 0:
                raise ValueError("ledger becomes negative at transaction %s" % transaction["txn_id"])

    return opening, parsed_transactions, complaint_by_utr, complaint_times, seizure_time


def analyze_attribution(case):
    """Return chronological attribution, complaint-order holds and totals.

    All monetary computations use Decimal. Amounts are rounded half-up to the
    nearest paisa only when rendered into the output contract.
    """
    opening, transactions, complaint_by_utr, complaint_times, seizure_time = _validate_case(case)
    complaints = case["complaints"]

    complaint_by_id = {item["complaint_id"]: item for item in complaints}
    rem = {item["complaint_id"]: Decimal("0") for item in complaints}
    forwarded = {item["complaint_id"]: Decimal("0") for item in complaints}
    forwarded_trace = {item["complaint_id"]: [] for item in complaints}
    pooled = {item["complaint_id"]: False for item in complaints}
    direct = {item["complaint_id"]: False for item in complaints}

    clean = opening
    ledger = opening
    last_taint_credit_time = None
    velocities = []
    epochs = []
    balance_history = []
    warnings = []
    balance_at_seizure = opening if seizure_time is not None else None

    for epoch_no, (timestamp, _, transaction, amount) in enumerate(transactions, start=1):
        txn_id = transaction["txn_id"]
        txn_type = transaction["type"]
        utr = transaction["utr"]
        if seizure_time is not None and timestamp > seizure_time:
            warnings.append("ACTIVITY_AFTER_SEIZURE: %s" % txn_id)

        if txn_type == "CREDIT":
            complaint = complaint_by_utr.get(utr)
            if complaint is not None:
                victim_id = complaint["complaint_id"]
                disputed = _parse_money(complaint["disputed_amount"], "complaint disputed_amount")
                taint = min(disputed, amount)
                rem[victim_id] += taint
                clean += amount - taint
                last_taint_credit_time = timestamp
                note = "Tainted credit of %s from %s" % (_money(taint), complaint["victim_label"])
            else:
                clean += amount
                note = "Clean credit"
            ledger += amount

        else:  # DEBIT: disputed-first is a documented project assumption.
            live_ids = [item["complaint_id"] for item in complaints if rem[item["complaint_id"]] > 0]
            total_taint = sum((rem[victim_id] for victim_id in live_ids), Decimal("0"))
            take = min(amount, total_taint)
            cuts = {}
            if take > 0 and total_taint > 0:
                pooled_event = len(live_ids) >= 2
                for victim_id in live_ids:
                    cut = take * rem[victim_id] / total_taint
                    if cut > rem[victim_id]:
                        cut = rem[victim_id]
                    rem[victim_id] -= cut
                    forwarded[victim_id] += cut
                    cuts[victim_id] = cut
                    if pooled_event:
                        pooled[victim_id] = True
                    else:
                        direct[victim_id] = True
                    if cut > 0:
                        forwarded_trace[victim_id].append({
                            "debit_txn_id": txn_id,
                            "debit_utr": utr,
                            "amount": _money(cut),
                            "timestamp": transaction["timestamp"],
                        })
                # Guard against tiny Decimal precision dust when all taint is consumed.
                if take == total_taint:
                    for victim_id in live_ids:
                        rem[victim_id] = Decimal("0")

            rest = amount - take
            clean -= rest
            ledger -= amount
            if clean < 0:
                warnings.append("NEGATIVE_CLEAN_BALANCE")

            if take > 0 and last_taint_credit_time is not None:
                delta = timestamp - last_taint_credit_time
                minutes = delta.days * 1440 + delta.seconds // 60
                if minutes < 0:
                    minutes = 0
                velocities.append(minutes)

            if take == 0:
                note = "Debit consumed clean money only"
            elif len(live_ids) >= 2:
                note = "Debit consumed %s of tainted money (pro-rata across %d victims)" % (_money(take), len(live_ids))
                if rest > 0:
                    note += "; debit of %s came from clean money" % _money(rest)
            else:
                note = "Debit consumed %s of tainted money (one victim)" % _money(take)
                if rest > 0:
                    note += "; debit of %s came from clean money" % _money(rest)

        epoch = {
            "epoch_no": epoch_no,
            "txn_id": txn_id,
            "timestamp": transaction["timestamp"],
            "event_type": txn_type,
            "event_amount": _money(amount),
            "event_utr": utr,
            "tainted_pool": {
                victim_id: _money(rem[victim_id])
                for victim_id in [item["complaint_id"] for item in complaints]
                if rem[victim_id] > 0
            },
            "clean_balance": _money(clean),
            "ledger_balance": _money(ledger),
            "note": note,
        }
        epochs.append(epoch)
        balance_history.append((timestamp, ledger))
        if seizure_time is not None and timestamp <= seizure_time:
            balance_at_seizure = ledger

    closing_balance = ledger
    if seizure_time is None:
        balance_at_seizure = closing_balance

    # Apply the SOP-style provisional holds in complaint timestamp order.
    held = Decimal("0")
    holds_sequence = []
    sop_hold_by_victim = {}
    sorted_complaints = sorted(
        enumerate(complaints), key=lambda item: (complaint_times[item[1]["complaint_id"]], item[0])
    )
    for order, (_, complaint) in enumerate(sorted_complaints, start=1):
        complaint_id = complaint["complaint_id"]
        complaint_time = complaint_times[complaint_id]
        balance_at_complaint = opening
        for transaction_time, transaction_balance in balance_history:
            if transaction_time <= complaint_time:
                balance_at_complaint = transaction_balance
            else:
                break
        available = max(balance_at_complaint - held, Decimal("0"))
        disputed = _parse_money(complaint["disputed_amount"], "complaint disputed_amount")
        hold_placed = min(disputed, available)
        held += hold_placed
        sop_hold_by_victim[complaint_id] = hold_placed
        holds_sequence.append({
            "order": order,
            "complaint_id": complaint_id,
            "complaint_timestamp": complaint["complaint_timestamp"],
            "disputed_amount": _money(disputed),
            "balance_available": _money(available),
            "hold_placed": _money(hold_placed),
        })

    victims = []
    rounded_restorable_sum = Decimal("0")
    forwarded_sum = Decimal("0")
    remaining_sum = sum(rem.values(), Decimal("0"))
    for complaint in complaints:
        victim_id = complaint["complaint_id"]
        disputed = _parse_money(complaint["disputed_amount"], "complaint disputed_amount")
        remaining = rem[victim_id]
        rounded_remaining = Decimal(_money(remaining))
        rounded_restorable_sum += rounded_remaining
        forwarded_sum += forwarded[victim_id]
        if pooled[victim_id]:
            method = "PRO_RATA"
        elif direct[victim_id]:
            method = "DIRECT"
        else:
            method = "INTACT"
        victims.append({
            "complaint_id": victim_id,
            "victim_label": complaint["victim_label"],
            "disputed_utr": complaint["disputed_utr"],
            "disputed_amount": _money(disputed),
            "attribution_method": method,
            "hold_in_current_account": _money(remaining),
            "restorable_amount": _money(remaining),
            "forwarded_downstream": _money(forwarded[victim_id]),
            "forwarded_trace": forwarded_trace[victim_id],
            "retention_ratio": _ratio(remaining / disputed),
            "sop_hold_amount": _money(sop_hold_by_victim.get(victim_id, Decimal("0"))),
        })

    clean_ring_fenced = closing_balance - remaining_sum
    clean_ring_fenced_rounded = Decimal(_money(clean_ring_fenced))
    rounded_closing = Decimal(_money(closing_balance))
    rounding_residual = rounded_closing - clean_ring_fenced_rounded - rounded_restorable_sum

    return {
        "case_id": case["case_id"],
        "opening_balance": _money(opening),
        "closing_balance": _money(closing_balance),
        "balance_at_seizure": _money(balance_at_seizure),
        "epochs": epochs,
        "holds_sequence": holds_sequence,
        "victims": victims,
        "clean_ring_fenced": _money(clean_ring_fenced),
        "metrics": {"min_pass_through_minutes": min(velocities) if velocities else None},
        "totals": {
            "sop_complaint_order_hold_total": _money(sum((Decimal(row["hold_placed"]) for row in holds_sequence), Decimal("0"))),
            "restorable_total": _money(rounded_restorable_sum),
            "mercy_right_sized_hold_total": _money(rounded_restorable_sum),
            "forwarded_downstream_total": _money(forwarded_sum),
            "rounding_residual": _money(rounding_residual),
        },
        "assumptions": list(ASSUMPTIONS),
        "warnings": warnings,
    }
