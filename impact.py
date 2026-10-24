"""Impact and relief quantification engine for Mercy Ledger.

Compares blanket account freezing against right-sized targeted liens,
measuring innocent capital preserved and victim recovery funds.
"""
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def _money(val):
    if not isinstance(val, Decimal):
        val = Decimal(str(val))
    return format(val.quantize(CENT, rounding=ROUND_HALF_UP), ".2f")


def case_impact(case, attribution, triage):
    """Compute before-and-after capital preservation impact for a single case."""
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

    bal_at_seizure = Decimal(
        attribution.get("balance_at_seizure") or attribution.get("closing_balance", "0.00")
    )
    blanket_total_locked = _money(bal_at_seizure)
    blanket_innocent_locked = _money(clean_balance)

    recommendation = triage.get("recommendation")
    if recommendation == "SEIZURE_S106":
        mercy_innocent_locked = _money(clean_balance)
    else:
        mercy_innocent_locked = "0.00"

    freed = Decimal(blanket_innocent_locked) - Decimal(mercy_innocent_locked)
    innocent_capital_freed = _money(freed)

    restorable = Decimal(attribution.get("totals", {}).get("restorable_total", "0.00"))
    victim_preserved = _money(restorable)
    victim_in_blanket = _money(restorable)

    return {
        "blanket_innocent_locked": blanket_innocent_locked,
        "blanket_total_locked": blanket_total_locked,
        "case_id": case["case_id"],
        "innocent_capital_freed": innocent_capital_freed,
        "mercy_innocent_locked": mercy_innocent_locked,
        "recommendation": recommendation,
        "title": case["title"],
        "victim_recoverable_in_blanket": victim_in_blanket,
        "victim_recoverable_preserved": victim_preserved,
    }


def aggregate_impact(items):
    """Aggregate capital preservation metrics across a list of case impact dicts."""
    if not items:
        return {
            "blanket_innocent_locked": "0.00",
            "by_recommendation": {},
            "cases": 0,
            "innocent_capital_freed": "0.00",
            "mercy_innocent_locked": "0.00",
            "per_case": [],
            "reduction_percent": "0.00",
            "victim_funds_preserved_percent": "100.00",
            "victim_recoverable_in_blanket": "0.00",
            "victim_recoverable_preserved": "0.00",
        }

    blanket_sum = sum((Decimal(i["blanket_innocent_locked"]) for i in items), Decimal("0"))
    mercy_sum = sum((Decimal(i["mercy_innocent_locked"]) for i in items), Decimal("0"))
    freed_sum = sum((Decimal(i["innocent_capital_freed"]) for i in items), Decimal("0"))
    victim_in_blanket_sum = sum((Decimal(i["victim_recoverable_in_blanket"]) for i in items), Decimal("0"))
    victim_preserved_sum = sum((Decimal(i["victim_recoverable_preserved"]) for i in items), Decimal("0"))

    if blanket_sum == Decimal("0"):
        reduction_percent = "0.00"
    else:
        reduction_dec = ((blanket_sum - mercy_sum) * Decimal("100") / blanket_sum).quantize(
            CENT, rounding=ROUND_HALF_UP
        )
        reduction_percent = format(reduction_dec, ".2f")

    if victim_preserved_sum == victim_in_blanket_sum:
        victim_funds_preserved_percent = "100.00"
    else:
        victim_funds_preserved_percent = "<100"

    by_rec = {}
    for i in items:
        rec = i.get("recommendation")
        if rec:
            by_rec[rec] = by_rec.get(rec, 0) + 1

    by_rec = dict(sorted(by_rec.items()))

    return {
        "blanket_innocent_locked": _money(blanket_sum),
        "by_recommendation": by_rec,
        "cases": len(items),
        "innocent_capital_freed": _money(freed_sum),
        "mercy_innocent_locked": _money(mercy_sum),
        "per_case": list(items),
        "reduction_percent": reduction_percent,
        "victim_funds_preserved_percent": victim_funds_preserved_percent,
        "victim_recoverable_in_blanket": _money(victim_in_blanket_sum),
        "victim_recoverable_preserved": _money(victim_preserved_sum),
    }
