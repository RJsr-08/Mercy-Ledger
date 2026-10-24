"""Triage and recommendation engine for Mercy Ledger.

Decision-support scorecard calculating policy recommendations based on
complaint velocity, clean balance share, pass-through speed, account type,
and merchant invoice documentation.
"""
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")
TEN_PERCENT = Decimal("0.10")

DISCLAIMER = (
    "Decision support only. Deterministic rules, not a trained model and "
    "not validated on real bank data. The Investigating Officer decides."
)

CITATIONS_SPECIAL = [
    "SOP Para 9.1(iii): for nodal/pool/escrow accounts only the disputed amount is held; LEAs should normally refrain from suspension or seizure",
    "SOP Para 5(xiii) and Annexure-V: direct attribution where possible, pro-rata where commingled",
    "SOP Para 5(ix): unwarranted freezing orders are discouraged",
]

CITATIONS_TARGETED = [
    "SOP Para 9.1(i): suspension/seizure applies where an account is reported multiple times, on lawful LEA direction under S.106 BNSS",
    "SOP Para 5(xiii) and Annexure-V: direct attribution where possible, pro-rata where commingled",
    "SOP Para 5(ix): unwarranted freezing orders are discouraged",
]

CITATIONS_SUSPENSION_OR_SEIZURE = [
    "SOP Para 9.1(i): suspension/seizure applies where an account is reported multiple times, on lawful LEA direction under S.106 BNSS",
    "SOP Para 9.1(vi) and 5(vi): reported accounts are subject to Enhanced Due Diligence (S.12AA PMLA)",
    "SOP Para 5(xiii) and Annexure-V: direct attribution where possible, pro-rata where commingled",
    "SOP Para 5(ix): unwarranted freezing orders are discouraged",
]

THRESHOLDS = {
    "fast_pass_through_minutes": 30,
    "seizure_at_or_above": 5,
    "suspension_at_or_above": 3,
}


def triage(case, attribution, grievance=None):
    """Compute triage recommendation, score, metrics, and factors."""
    complaints = case.get("complaints", [])
    n = len(complaints)

    account_type = case.get("account", {}).get("account_type", "")
    special = account_type in ("NODAL", "POOL", "ESCROW")

    docs = False
    if isinstance(grievance, dict):
        docs = bool(grievance.get("all_disputed_matched", False))

    seizure_ts = case.get("seizure_timestamp")
    clean_balance = None
    if seizure_ts:
        for ep in reversed(attribution.get("epochs", [])):
            if ep["timestamp"] <= seizure_ts:
                clean_balance = Decimal(ep["clean_balance"])
                break
        if clean_balance is None:
            clean_balance = Decimal(case.get("opening_balance", "0.00"))
    else:
        epochs = attribution.get("epochs", [])
        if epochs:
            clean_balance = Decimal(epochs[-1]["clean_balance"])
        else:
            clean_balance = Decimal(case.get("opening_balance", "0.00"))

    bal_at_seizure = Decimal(attribution.get("balance_at_seizure", "0.00"))

    if bal_at_seizure <= Decimal("0"):
        clean_share_rounded = Decimal("0.0000")
    else:
        clean_share_rounded = (clean_balance / bal_at_seizure).quantize(
            FOUR_PLACES, rounding=ROUND_HALF_UP
        )
    clean_share_str = format(clean_share_rounded, ".4f")

    min_pass_through_minutes = attribution.get("metrics", {}).get("min_pass_through_minutes")
    fast = (min_pass_through_minutes is not None and min_pass_through_minutes <= 30)

    lowclean = (clean_share_rounded < TEN_PERCENT)

    factors = [
        {
            "key": "victims3",
            "label": "3 or more distinct complaints",
            "points": 2 if n >= 3 else 0,
            "triggered": bool(n >= 3),
        },
        {
            "key": "victims2",
            "label": "Exactly 2 distinct complaints",
            "points": 1 if n == 2 else 0,
            "triggered": bool(n == 2),
        },
        {
            "key": "fast",
            "label": "Fast pass-through (tainted money left within 30 min)",
            "points": 2 if fast else 0,
            "triggered": bool(fast),
        },
        {
            "key": "lowclean",
            "label": "Clean balance is under 10% of account balance",
            "points": 1 if lowclean else 0,
            "triggered": bool(lowclean),
        },
        {
            "key": "nodocs",
            "label": "No merchant document matched to every disputed UTR",
            "points": 1 if not docs else 0,
            "triggered": bool(not docs),
        },
        {
            "key": "docs",
            "label": "Merchant documents match every disputed UTR",
            "points": -2 if docs else 0,
            "triggered": bool(docs),
        },
    ]

    score = sum(f["points"] for f in factors)

    if special:
        recommendation = "TARGETED_LIEN_ONLY"
        rationale = "Special (nodal/pool/escrow) account: hold the disputed amount only."
        citations = CITATIONS_SPECIAL
    elif n <= 1:
        recommendation = "TARGETED_LIEN_ONLY"
        rationale = "Only one complaint: the SOP escalates to suspension/seizure when an account is reported multiple times."
        citations = CITATIONS_TARGETED
    elif score >= 5:
        recommendation = "SEIZURE_S106"
        rationale = "High score: multiple victims with fast pass-through and little clean balance."
        citations = CITATIONS_SUSPENSION_OR_SEIZURE
    elif score >= 3:
        recommendation = "DIGITAL_SUSPENSION_PENDING_EDD"
        rationale = "Medium score: suspend digital channels pending Enhanced Due Diligence, keep branch access."
        citations = CITATIONS_SUSPENSION_OR_SEIZURE
    else:
        recommendation = "TARGETED_LIEN_ONLY"
        rationale = "Low score: hold the disputed amount only."
        citations = CITATIONS_TARGETED

    metrics = {
        "clean_share_of_balance": clean_share_str,
        "complaints_count": n,
        "documents_match_all": docs,
        "min_pass_through_minutes": min_pass_through_minutes,
        "special_account": special,
    }

    return {
        "case_id": case["case_id"],
        "citations": citations,
        "disclaimer": DISCLAIMER,
        "factors": factors,
        "human_signoff_required": True,
        "metrics": metrics,
        "rationale": rationale,
        "recommendation": recommendation,
        "score": score,
        "thresholds": THRESHOLDS,
    }
