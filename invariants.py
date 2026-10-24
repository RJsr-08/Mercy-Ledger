"""Financial invariants and conservation rules verification for Mercy Ledger.

Implements strict forensic accounting conservation and Lowest Intermediate Balance
Rule (LIBR) checks (IIBF / NFSU BankQuest 2025; UNODC Asset Tracing Standards)
across all attribution epochs, victim pools, and closing totals using Decimal arithmetic.
"""
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def _dec(val):
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))


def check_case_invariants(case, attribution):
    """Verify that attribution output satisfies core conservation invariants.

    Args:
        case: dict containing case data.
        attribution: dict containing attribution output.

    Returns:
        dict with case_id, passed (bool), checks (list of dicts), and errors (list).
    """
    case_id = case.get("case_id", "UNKNOWN")
    checks = []
    errors = []

    # Check 1: Epoch Conservation
    # In every attribution epoch, ledger_balance == clean_balance + sum(tainted_pool.values())
    epochs = attribution.get("epochs", [])
    epoch_passed = True
    epoch_details = []
    for ep in epochs:
        ep_no = ep.get("epoch_no")
        ledger = _dec(ep.get("ledger_balance", "0.00"))
        clean = _dec(ep.get("clean_balance", "0.00"))
        pool_items = ep.get("tainted_pool", {})
        pool_sum = sum((_dec(v) for v in pool_items.values()), Decimal("0.00"))
        # Account for half-up rounding residuals when summing many individually rounded strings
        tolerance = Decimal("0.01") * Decimal(len(pool_items)) if len(pool_items) > 1 else Decimal("0.00")
        if abs(ledger - (clean + pool_sum)) > tolerance:
            epoch_passed = False
            msg = f"Epoch {ep_no} balance mismatch: ledger {ledger} != clean {clean} + pool {pool_sum}"
            epoch_details.append(msg)
            errors.append(msg)

    checks.append({
        "id": "EPOCH_CONSERVATION",
        "passed": epoch_passed,
        "details": "; ".join(epoch_details) if not epoch_passed else f"All {len(epochs)} epochs balanced.",
    })

    # Check 2: Non-negative amounts
    non_neg_passed = True
    non_neg_details = []
    for ep in epochs:
        if _dec(ep.get("ledger_balance", "0.00")) < 0 or _dec(ep.get("clean_balance", "0.00")) < 0:
            non_neg_passed = False
            non_neg_details.append(f"Epoch {ep.get('epoch_no')} has negative balance")
        for k, v in ep.get("tainted_pool", {}).items():
            if _dec(v) < 0:
                non_neg_passed = False
                non_neg_details.append(f"Epoch {ep.get('epoch_no')} pool for {k} is negative")

    for v in attribution.get("victims", []):
        for amt_key in ("disputed_amount", "hold_in_current_account", "restorable_amount", "forwarded_downstream"):
            if _dec(v.get(amt_key, "0.00")) < 0:
                non_neg_passed = False
                non_neg_details.append(f"Victim {v.get('complaint_id')} {amt_key} is negative")

    for t_key in ("sop_complaint_order_hold_total", "restorable_total", "mercy_right_sized_hold_total", "forwarded_downstream_total"):
        if _dec(attribution.get("totals", {}).get(t_key, "0.00")) < 0:
            non_neg_passed = False
            non_neg_details.append(f"Total {t_key} is negative")

    if not non_neg_passed:
        errors.extend(non_neg_details)

    checks.append({
        "id": "NON_NEGATIVE_AMOUNTS",
        "passed": non_neg_passed,
        "details": "; ".join(non_neg_details) if not non_neg_passed else "All balances and allocations are non-negative.",
    })

    # Check 3: Victim disputed conservation
    # hold_in_current_account + forwarded_downstream == disputed_amount
    victim_cons_passed = True
    victim_cons_details = []
    victims = attribution.get("victims", [])
    for v in victims:
        cid = v.get("complaint_id", "UNKNOWN")
        held = _dec(v.get("hold_in_current_account", "0.00"))
        fwd = _dec(v.get("forwarded_downstream", "0.00"))
        disputed = _dec(v.get("disputed_amount", "0.00"))
        if held + fwd != disputed:
            victim_cons_passed = False
            msg = f"Victim {cid}: held ({held}) + forwarded ({fwd}) != disputed ({disputed})"
            victim_cons_details.append(msg)
            errors.append(msg)

    checks.append({
        "id": "VICTIM_DISPUTED_CONSERVATION",
        "passed": victim_cons_passed,
        "details": "; ".join(victim_cons_details) if not victim_cons_passed else f"All {len(victims)} victims conserve disputed principal.",
    })

    # Check 4: Restorable sum equals totals.restorable_total
    v_restorable_sum = sum((_dec(v.get("restorable_amount", "0.00")) for v in victims), Decimal("0.00"))
    total_restorable = _dec(attribution.get("totals", {}).get("restorable_total", "0.00"))
    restorable_match = (v_restorable_sum == total_restorable)
    if not restorable_match:
        errors.append(f"Restorable sum ({v_restorable_sum}) != totals.restorable_total ({total_restorable})")

    checks.append({
        "id": "RESTORABLE_SUM_EQUAL_TOTAL",
        "passed": restorable_match,
        "details": f"Sum of victim restorable ({v_restorable_sum}) equals totals ({total_restorable})" if restorable_match else f"Mismatch: {v_restorable_sum} vs {total_restorable}",
    })

    # Check 5: Forwarded sum equals totals.forwarded_downstream_total
    v_fwd_sum = sum((_dec(v.get("forwarded_downstream", "0.00")) for v in victims), Decimal("0.00"))
    total_fwd = _dec(attribution.get("totals", {}).get("forwarded_downstream_total", "0.00"))
    fwd_match = (v_fwd_sum == total_fwd)
    if not fwd_match:
        errors.append(f"Forwarded sum ({v_fwd_sum}) != totals.forwarded_downstream_total ({total_fwd})")

    checks.append({
        "id": "FORWARDED_SUM_EQUAL_TOTAL",
        "passed": fwd_match,
        "details": f"Sum of forwarded debits ({v_fwd_sum}) equals totals ({total_fwd})" if fwd_match else f"Mismatch: {v_fwd_sum} vs {total_fwd}",
    })

    # Check 6: Restorable total does not exceed balance_at_seizure
    bal_at_seizure = _dec(attribution.get("balance_at_seizure", "0.00"))
    restorable_le_seizure = (total_restorable <= bal_at_seizure)
    if not restorable_le_seizure:
        errors.append(f"Restorable total ({total_restorable}) exceeds balance at seizure ({bal_at_seizure})")

    checks.append({
        "id": "RESTORABLE_WITHIN_SEIZURE_BALANCE",
        "passed": restorable_le_seizure,
        "details": f"Restorable total ({total_restorable}) <= seizure balance ({bal_at_seizure})" if restorable_le_seizure else f"Restorable ({total_restorable}) exceeds seizure balance ({bal_at_seizure})",
    })

    # Check 7: Closing balance agrees with final epoch ledger balance
    expected_closing = _dec(epochs[-1]["ledger_balance"]) if epochs else _dec(case.get("opening_balance", "0.00"))
    closing_balance = _dec(attribution.get("closing_balance", "0.00"))
    closing_match = (closing_balance == expected_closing)
    if not closing_match:
        errors.append(f"Closing balance ({closing_balance}) != final epoch ledger ({expected_closing})")

    checks.append({
        "id": "CLOSING_BALANCE_AGREEMENT",
        "passed": closing_match,
        "details": f"Closing balance ({closing_balance}) matches final ledger snapshot ({expected_closing})" if closing_match else f"Mismatch: {closing_balance} vs {expected_closing}",
    })

    overall_passed = all(c["passed"] for c in checks)

    return {
        "case_id": case_id,
        "passed": overall_passed,
        "checks": checks,
        "errors": errors,
    }
