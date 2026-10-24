"""
simulator.py  --  Synthetic Case Simulator for Mercy Ledger.
Owner: Teammate A.

Implements generate_cases(n, seed) -> list[case].
All money is a STRING with exactly two decimal places.
Uses random.Random(seed) only; no global random state.
No network, no AI calls, no file I/O, no system clock, no extra packages.
Synthetic cases are for software stress-testing only and do not demonstrate
real-world fraud rates, classifier accuracy or legal outcomes.
"""

import random
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

_ACCOUNT_TYPES_SAVINGS = ["SAVINGS"]
_ACCOUNT_TYPES_MERCHANT = ["CURRENT"]
_ALL_ACCOUNT_TYPES = ["SAVINGS", "CURRENT", "NODAL", "POOL", "ESCROW"]

_STATES = [
    "Andhra Pradesh", "Bihar", "Delhi", "Gujarat", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Rajasthan", "Tamil Nadu",
    "Telangana", "Uttar Pradesh", "West Bengal", "Haryana", "Punjab",
]

_HOLDER_NAMES = [
    "Ramesh Kumar", "Sunita Devi", "Anil Sharma", "Priya Singh",
    "Mohammed Ali", "Kavita Rao", "Suresh Gupta", "Meena Nair",
    "Amit Patel", "Deepa Menon", "Vijay Reddy", "Lalitha Krishnan",
    "Rajesh Verma", "Anita Joshi", "Sanjay Mishra", "Pooja Yadav",
]

_MERCHANT_NAMES = [
    "Example Enterprises Pvt Ltd", "Sample Traders", "Demo Goods Co",
    "Test Merchant Solutions", "Illustrative Retail Ltd",
    "Synthetic Commerce LLP", "Model Business Services",
]

_NARRATIONS_CREDIT = [
    "UPI transfer received", "NEFT credit", "IMPS credit",
    "Online transfer", "Payment received", "Fund transfer in",
    "Credit received", "Inward remittance",
]

_NARRATIONS_DEBIT = [
    "UPI transfer sent", "NEFT debit", "IMPS debit",
    "Outgoing transfer", "Withdrawal", "Fund transfer out",
    "Payment sent", "Debit transaction",
]


def _money_str(d):
    """Convert a Decimal to a two-decimal money string."""
    return format(d.quantize(CENT, rounding=ROUND_HALF_UP), ".2f")


def _rand_money(rng, lo, hi):
    """
    Return a Decimal money value in [lo, hi] (inclusive) rounded to two decimal places.
    lo and hi may be int, Decimal, or anything with __mul__ by int (no float allowed).
    """
    # Convert to integer cents using Decimal arithmetic — no float()
    lo_d = Decimal(str(lo)) if not isinstance(lo, Decimal) else lo
    hi_d = Decimal(str(hi)) if not isinstance(hi, Decimal) else hi
    lo_cents = int((lo_d * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    hi_cents = int((hi_d * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if lo_cents > hi_cents:
        lo_cents, hi_cents = hi_cents, lo_cents
    if lo_cents == hi_cents:
        return Decimal(lo_cents) / Decimal(100)
    cents = rng.randint(lo_cents, hi_cents)
    return Decimal(cents) / Decimal(100)


def _base_date(rng):
    """Pick a deterministic base year/month/day from a fixed range; no system clock."""
    year = 2025
    month = rng.randint(1, 12)
    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day = rng.randint(1, days_in_month[month])
    return (year, month, day)


def _iso_date(y, m, d):
    return "%04d-%02d-%02d" % (y, m, d)


def _add_days(y, m, d, n):
    """Add n days to (y, m, d) — pure-Python date arithmetic, no datetime module."""
    _DIM = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def is_leap(yr):
        return (yr % 4 == 0 and yr % 100 != 0) or (yr % 400 == 0)

    def days_in_month(yr, mo):
        if mo == 2 and is_leap(yr):
            return 29
        return _DIM[mo]

    d += n
    while d > days_in_month(y, m):
        d -= days_in_month(y, m)
        m += 1
        if m > 12:
            m = 1
            y += 1
    while d < 1:
        m -= 1
        if m < 1:
            m = 12
            y -= 1
        d += days_in_month(y, m)
    return (y, m, d)


def _iso_ts(y, m, d, hh, mm, ss):
    return "%04d-%02d-%02dT%02d:%02d:%02d" % (y, m, d, hh, mm, ss)


def _generate_merchant_case(idx, rng):
    """
    Generate a merchant-like case: CURRENT account, opening balance >= 100000,
    single complaint, small disputed amount (~200).
    """
    case_id = "SIM_%03d" % idx

    (by, bm, bd) = _base_date(rng)

    holder = rng.choice(_MERCHANT_NAMES)
    account_type = "CURRENT"
    layer = rng.randint(2, 4)
    account_id = "SIM-ACC-%03d" % idx

    # Opening balance: 100000 to 600000
    opening_balance = _rand_money(rng, 100000, 600000)

    # Disputed credit: small amount 100 to 500
    disputed_amount = _rand_money(rng, 100, 500)

    transactions = []
    txn_counter = [0]
    utr_counter = [0]
    balance = opening_balance

    def next_txn_id():
        txn_counter[0] += 1
        return "T%d" % txn_counter[0]

    def next_utr(prefix):
        utr_counter[0] += 1
        return "%s-%03d" % (prefix, utr_counter[0])

    # Build timestamps: start at 09:00 on base date, advance by minutes
    minute_offset = [60]   # start at 09:00 (offset from 08:00)

    def next_ts(extra_min=None):
        if extra_min is None:
            extra_min = rng.randint(10, 90)
        minute_offset[0] += extra_min
        total = minute_offset[0]
        # Keep within a reasonable business-day window (8h -> 20h)
        hh = 8 + (total // 60) % 12
        mm = total % 60
        ss = rng.randint(0, 59)
        return _iso_ts(by, bm, bd, hh, mm, ss)

    # Optional: one or two extra clean credits before the disputed credit
    extra_credits = rng.randint(0, 2)
    for _ in range(extra_credits):
        amt = _rand_money(rng, 1000, 50000)
        ts = next_ts()
        utr = next_utr("UTR-SIM%03d-CL" % idx)
        transactions.append({
            "txn_id": next_txn_id(),
            "timestamp": ts,
            "type": "CREDIT",
            "amount": _money_str(amt),
            "utr": utr,
            "narration": rng.choice(_NARRATIONS_CREDIT),
        })
        balance += amt

    # The single disputed credit
    disputed_utr = next_utr("UTR-SIM%03d-D" % idx)
    disputed_ts = next_ts()
    transactions.append({
        "txn_id": next_txn_id(),
        "timestamp": disputed_ts,
        "type": "CREDIT",
        "amount": _money_str(disputed_amount),
        "utr": disputed_utr,
        "narration": "UPI payment received for goods",
    })
    balance += disputed_amount

    # Optional small clean debit after the disputed credit
    if rng.random() < 0.4 and balance > Decimal("500"):
        debit_max = balance - Decimal("10")
        debit_hi = min(debit_max, Decimal("5000"))
        if debit_hi >= Decimal("10"):
            debit_amt = _rand_money(rng, 10, debit_hi)
            debit_ts = next_ts()
            transactions.append({
                "txn_id": next_txn_id(),
                "timestamp": debit_ts,
                "type": "DEBIT",
                "amount": _money_str(debit_amt),
                "utr": next_utr("OUT-SIM%03d" % idx),
                "narration": rng.choice(_NARRATIONS_DEBIT),
            })
            balance -= debit_amt

    # Complaint: at least 1 hour after the disputed credit, complaint is next day
    comp_day_offset = rng.randint(0, 2)
    (cy, cm, cd) = _add_days(by, bm, bd, max(1, comp_day_offset))
    comp_hh = rng.randint(10, 18)
    comp_mm = rng.randint(0, 59)
    comp_ss = rng.randint(0, 59)
    complaint_ts = _iso_ts(cy, cm, cd, comp_hh, comp_mm, comp_ss)

    complaints = [{
        "complaint_id": "SIM%03d-P1" % idx,
        "victim_label": "Complainant P1",
        "state": rng.choice(_STATES),
        "disputed_utr": disputed_utr,
        "disputed_amount": _money_str(disputed_amount),
        "complaint_timestamp": complaint_ts,
    }]

    # Seizure: 1-3 days after base date
    (sy, sm, sd) = _add_days(by, bm, bd, rng.randint(1, 3))
    seizure_ts = _iso_ts(sy, sm, sd, 9 + rng.randint(0, 4), rng.randint(0, 59), 0)

    # demo_today: 3-10 days after seizure
    (ty, tm, td) = _add_days(sy, sm, sd, rng.randint(3, 10))
    demo_today = _iso_date(ty, tm, td)

    # sla_context with all five keys
    (d1y, d1m, d1d) = _add_days(sy, sm, sd, rng.randint(0, 2))
    sla_context = {
        "account_holder_complaint_on": _iso_date(d1y, d1m, d1d) if rng.random() < 0.7 else None,
        "grievance_filed_on": None,
        "io_decision_on": None,
        "io_direction_on": None,
        "suspension_started_on": _iso_date(sy, sm, sd),
    }

    return {
        "case_id": case_id,
        "tier": 3,
        "title": "Synthetic merchant case %s" % case_id,
        "description": (
            "Synthetic case generated for software stress-testing only. "
            "Not based on real-world data. Not a representation of actual fraud rates or legal outcomes."
        ),
        "demo_today": demo_today,
        "account": {
            "account_id": account_id,
            "account_type": account_type,
            "layer": layer,
            "holder_name": holder,
        },
        "opening_balance": _money_str(opening_balance),
        "transactions": transactions,
        "complaints": complaints,
        "seizure_timestamp": seizure_ts,
        "sla_context": sla_context,
        "invoices": [],
    }


def _generate_multi_victim_case(idx, rng):
    """
    Generate a multi-victim case: SAVINGS/CURRENT, 2-6 victims,
    some partial debit scenarios, lower opening balance.
    """
    case_id = "SIM_%03d" % idx

    (by, bm, bd) = _base_date(rng)

    account_type = rng.choice(["SAVINGS", "SAVINGS", "SAVINGS", "CURRENT"])
    layer = rng.randint(1, 3)
    account_id = "SIM-ACC-%03d" % idx
    holder = rng.choice(_HOLDER_NAMES)

    # Opening balance: 0 to 5000
    opening_balance = _rand_money(rng, 0, 5000)
    balance = opening_balance

    # Number of victims: 2-6
    num_victims = rng.randint(2, 6)

    transactions = []
    txn_counter = [0]
    utr_counter = [0]

    def next_txn_id():
        txn_counter[0] += 1
        return "T%d" % txn_counter[0]

    def next_utr(prefix):
        utr_counter[0] += 1
        return "%s-%03d" % (prefix, utr_counter[0])

    # Timestamps start at 09:00 on the base date
    minute_offset = [60]  # 60 minutes after 08:00 = 09:00

    def next_ts(extra_min=None):
        if extra_min is None:
            extra_min = rng.randint(5, 60)
        minute_offset[0] += extra_min
        total = minute_offset[0]
        hh = 8 + (total // 60) % 12   # keep within 08:00-19:59
        mm = total % 60
        ss = rng.randint(0, 59)
        return _iso_ts(by, bm, bd, hh, mm, ss)

    # Generate victim credit amounts (5000 to 150000)
    victim_amounts = [_rand_money(rng, 5000, 150000) for _ in range(num_victims)]

    disputed_utrs = []
    credit_timestamps = []

    for vi in range(num_victims):
        # Occasionally insert a clean credit before this victim credit
        if rng.random() < 0.25:
            clean_amt = _rand_money(rng, 500, 10000)
            ts = next_ts()
            transactions.append({
                "txn_id": next_txn_id(),
                "timestamp": ts,
                "type": "CREDIT",
                "amount": _money_str(clean_amt),
                "utr": next_utr("UTR-SIM%03d-CL" % idx),
                "narration": rng.choice(_NARRATIONS_CREDIT),
            })
            balance += clean_amt

        # Victim credit
        utr = next_utr("UTR-SIM%03d-V%d" % (idx, vi + 1))
        disputed_utrs.append(utr)
        ts = next_ts()
        credit_timestamps.append(ts)
        transactions.append({
            "txn_id": next_txn_id(),
            "timestamp": ts,
            "type": "CREDIT",
            "amount": _money_str(victim_amounts[vi]),
            "utr": utr,
            "narration": "Credit from victim %d" % (vi + 1),
        })
        balance += victim_amounts[vi]

        # Optionally debit some of the balance (partial consumption)
        if rng.random() < 0.5 and balance > Decimal("100"):
            # Debit up to 90% of balance but always keep at least 0
            max_debit = balance * Decimal("9") / Decimal("10")
            max_debit = max_debit.quantize(CENT, rounding=ROUND_HALF_UP)
            if max_debit >= Decimal("1"):
                debit_amt = _rand_money(rng, 1, max_debit)
                debit_amt = min(debit_amt, balance)
                if debit_amt > Decimal("0"):
                    ts = next_ts()
                    transactions.append({
                        "txn_id": next_txn_id(),
                        "timestamp": ts,
                        "type": "DEBIT",
                        "amount": _money_str(debit_amt),
                        "utr": next_utr("OUT-SIM%03d" % idx),
                        "narration": rng.choice(_NARRATIONS_DEBIT),
                    })
                    balance -= debit_amt

    # Build complaints: one per victim, timestamp after the corresponding credit
    complaints = []
    for vi in range(num_victims):
        comp_id = "SIM%03d-C%d" % (idx, vi + 1)
        # Complaint is 1 or 2 days after the base date (chronologically after the credit)
        comp_day_offset = rng.randint(1, 3)
        (cy, cm, cd) = _add_days(by, bm, bd, comp_day_offset)
        comp_hh = rng.randint(8, 20)
        comp_mm = rng.randint(0, 59)
        comp_ss = rng.randint(0, 59)
        comp_ts = _iso_ts(cy, cm, cd, comp_hh, comp_mm, comp_ss)

        complaints.append({
            "complaint_id": comp_id,
            "victim_label": "Victim %d" % (vi + 1),
            "state": rng.choice(_STATES),
            "disputed_utr": disputed_utrs[vi],
            "disputed_amount": _money_str(victim_amounts[vi]),
            "complaint_timestamp": comp_ts,
        })

    # Seizure: 1-5 days after base date
    (sy, sm, sd) = _add_days(by, bm, bd, rng.randint(1, 5))
    seizure_ts = _iso_ts(sy, sm, sd, 9 + rng.randint(0, 6), rng.randint(0, 30), 0)

    # demo_today: 3-15 days after seizure
    (ty, tm, td) = _add_days(sy, sm, sd, rng.randint(3, 15))
    demo_today = _iso_date(ty, tm, td)

    # sla_context — all five keys, some may be None
    has_ah_complaint = rng.random() < 0.6
    has_grievance = rng.random() < 0.5
    has_io_decision = rng.random() < 0.3
    has_io_direction = rng.random() < 0.3
    has_suspension = rng.random() < 0.8

    (d1y, d1m, d1d) = _add_days(sy, sm, sd, rng.randint(0, 3))
    (d2y, d2m, d2d) = _add_days(d1y, d1m, d1d, rng.randint(1, 5))
    (d3y, d3m, d3d) = _add_days(d2y, d2m, d2d, rng.randint(1, 7))
    (d4y, d4m, d4d) = _add_days(d3y, d3m, d3d, rng.randint(1, 5))

    sla_context = {
        "account_holder_complaint_on": _iso_date(d1y, d1m, d1d) if has_ah_complaint else None,
        "grievance_filed_on": _iso_date(d2y, d2m, d2d) if has_grievance else None,
        "io_decision_on": _iso_date(d3y, d3m, d3d) if has_io_decision else None,
        "io_direction_on": _iso_date(d4y, d4m, d4d) if has_io_direction else None,
        "suspension_started_on": _iso_date(sy, sm, sd) if has_suspension else None,
    }

    return {
        "case_id": case_id,
        "tier": 3,
        "title": "Synthetic multi-victim case %s" % case_id,
        "description": (
            "Synthetic case generated for software stress-testing only. "
            "Not based on real-world data. Not a representation of actual fraud rates or legal outcomes."
        ),
        "demo_today": demo_today,
        "account": {
            "account_id": account_id,
            "account_type": account_type,
            "layer": layer,
            "holder_name": holder,
        },
        "opening_balance": _money_str(opening_balance),
        "transactions": transactions,
        "complaints": complaints,
        "seizure_timestamp": seizure_ts,
        "sla_context": sla_context,
        "invoices": [],
    }


def generate_cases(n, seed):
    """
    Generate n deterministic synthetic Mercy Ledger cases using random.Random(seed).

    Returns a list of n CASE dicts conforming to the 01_DATA_CONTRACT schema.
    Same (n, seed) always produces identical output.
    Different seeds should produce different output.

    These cases are for software stress-testing only and do not model real-world
    fraud rates, classifier accuracy or legal outcomes.
    """
    rng = random.Random(seed)

    cases = []
    for i in range(n):
        # Roughly 1 in 4 cases is merchant-like (CURRENT, high balance, 1 complaint)
        if rng.random() < 0.25:
            case = _generate_merchant_case(i, rng)
        else:
            case = _generate_multi_victim_case(i, rng)

        cases.append(case)

    return cases
