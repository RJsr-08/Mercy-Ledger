"""Attribution assumption sensitivity analysis for Mercy Ledger.

Operationalizes forensic accounting doctrines (IIBF / NFSU BankQuest 2025:
Clayton's Case FIFO, In re Hallett's Estate, and Sinclair v. Brougham pro-rata)
to explore how attribution outcomes shift under alternative debit-consumption
hypotheses: DISPUTED_FIRST (taint-first baseline), CLEAN_FIRST, and PROPORTIONAL.

This is a decision-support and sensitivity analysis tool, NOT an alternative legal rule,
official SOP policy, or binding determination of legally restorable funds.
"""
import copy
from decimal import Decimal, ROUND_HALF_UP, getcontext

getcontext().prec = 40

CENT = Decimal("0.01")

DISCLAIMER = (
    "Hypothetical sensitivity analysis only. Demonstrates how debit-consumption "
    "accounting assumptions impact balance distribution. This is not an official "
    "SOP policy, legal rule, or binding restitution determination. Figures represent "
    "model scenario allocations, not money legally recoverable or legally due."
)

SCENARIO_RULES = {
    "DISPUTED_FIRST": (
        "Consumes disputed/attributed pools before clean balance. "
        "Baseline taint-first assumption where fraudulent withdrawals deplete illicit funds first."
    ),
    "CLEAN_FIRST": (
        "Consumes available clean balance before touching disputed/attributed funds. "
        "Depletes innocent account capital prior to withdrawing disputed balances."
    ),
    "PROPORTIONAL": (
        "Consumes clean and disputed balances proportionally to their available shares "
        "at the moment of each debit transaction."
    ),
}

SCENARIO_LIMITATIONS = {
    "DISPUTED_FIRST": [
        "Assumes fraudulent outflows exhaust illicit credits before touching legitimate capital.",
        "Commingled multi-victim debits require pro-rata allocation assumptions.",
    ],
    "CLEAN_FIRST": [
        "Depletes innocent account holder funds before disputed deposits.",
        "Substantially reduces clean ring-fencing for active operating accounts.",
    ],
    "PROPORTIONAL": [
        "Treats all co-present funds as fungibly mixed at the exact moment of debit.",
        "Highly sensitive to fine-grained timestamp ordering and timing of interleaved deposits.",
    ],
}


def _money(val):
    if not isinstance(val, Decimal):
        val = Decimal(str(val))
    return format(val.quantize(CENT, rounding=ROUND_HALF_UP), ".2f")


def _simulate_scenario(case, policy):
    """Simulate a single debit-consumption scenario."""
    opening = Decimal(str(case.get("opening_balance", "0.00")))
    clean = opening
    complaints = case.get("complaints", [])
    rem = {c["complaint_id"]: Decimal("0.00") for c in complaints if "complaint_id" in c}
    complaint_by_utr = {c["disputed_utr"]: c for c in complaints if "disputed_utr" in c}

    txns = sorted(case.get("transactions", []), key=lambda t: t.get("timestamp", ""))
    ledger = opening

    errors = []

    for t in txns:
        amt = Decimal(str(t.get("amount", "0.00")))
        txn_type = t.get("type")

        if txn_type == "CREDIT":
            utr = t.get("utr")
            matched_c = complaint_by_utr.get(utr)
            if matched_c:
                cid = matched_c["complaint_id"]
                disputed = Decimal(str(matched_c.get("disputed_amount", "0.00")))
                taint = min(disputed, amt)
                rem[cid] += taint
                clean += (amt - taint)
            else:
                clean += amt
            ledger += amt

        elif txn_type == "DEBIT":
            live_ids = [cid for cid, bal in rem.items() if bal > Decimal("0")]
            total_taint = sum((rem[cid] for cid in live_ids), Decimal("0"))

            if policy == "DISPUTED_FIRST":
                take_disputed = min(amt, total_taint)
                take_clean = amt - take_disputed
            elif policy == "CLEAN_FIRST":
                take_clean = min(amt, clean)
                take_disputed = min(amt - take_clean, total_taint)
            elif policy == "PROPORTIONAL":
                avail = clean + total_taint
                if avail > Decimal("0"):
                    take = min(amt, avail)
                    take_clean = min(clean, (take * clean) / avail)
                    take_disputed = min(total_taint, take - take_clean)
                else:
                    take_clean = amt
                    take_disputed = Decimal("0")
            else:
                take_disputed = Decimal("0")
                take_clean = amt
                errors.append(f"Unknown policy {policy}")

            if take_disputed > Decimal("0") and total_taint > Decimal("0"):
                for cid in live_ids:
                    cut = (take_disputed * rem[cid]) / total_taint
                    if cut > rem[cid]:
                        cut = rem[cid]
                    rem[cid] -= cut
                if take_disputed == total_taint:
                    for cid in live_ids:
                        rem[cid] = Decimal("0.00")

            clean -= take_clean
            ledger -= amt

    total_attr = sum(rem.values(), Decimal("0.00"))
    recon_diff = ledger - clean - total_attr

    return {
        "name": policy,
        "rule": SCENARIO_RULES.get(policy, ""),
        "scenario_remaining_clean": _money(clean),
        "scenario_remaining_attributed": {cid: _money(bal) for cid, bal in rem.items()},
        "total_scenario_attributed": _money(total_attr),
        "closing_ledger_balance": _money(ledger),
        "reconciliation_difference": _money(recon_diff),
        "limitations": SCENARIO_LIMITATIONS.get(policy, []),
        "errors": errors,
    }


def analyze_sensitivity(case, baseline_attribution=None):
    """Analyze impact of alternative debit consumption rules on attribution."""
    if not isinstance(case, dict) or "case_id" not in case:
        return {
            "case_id": "UNKNOWN",
            "baseline_validated": False,
            "validation_error": "Invalid case input: must be a dict with case_id",
            "disclaimer": DISCLAIMER,
            "scenarios": {},
            "summary": "Sensitivity analysis failed: invalid case input.",
        }

    case_id = case.get("case_id", "UNKNOWN")

    # Deepcopy to guarantee pure execution without mutating inputs
    case_clean = copy.deepcopy(case)

    # Compute the 3 scenarios
    scenarios = {}
    for policy in ("DISPUTED_FIRST", "CLEAN_FIRST", "PROPORTIONAL"):
        scenarios[policy] = _simulate_scenario(case_clean, policy)

    # Validate DISPUTED_FIRST against baseline attribution
    if baseline_attribution is None:
        try:
            import attribution
            baseline_attribution = attribution.analyze_attribution(case_clean)
        except Exception as exc:
            baseline_attribution = None

    baseline_validated = True
    validation_error = None

    if baseline_attribution is not None and isinstance(baseline_attribution, dict):
        base_clean = baseline_attribution.get("clean_ring_fenced")
        base_totals = baseline_attribution.get("totals", {})
        base_restorable = base_totals.get("restorable_total")

        disp_first = scenarios["DISPUTED_FIRST"]

        if base_clean is not None and disp_first["scenario_remaining_clean"] != base_clean:
            baseline_validated = False
            validation_error = (
                f"DISPUTED_FIRST clean balance ({disp_first['scenario_remaining_clean']}) "
                f"mismatches baseline ({base_clean})"
            )

        if base_restorable is not None and disp_first["total_scenario_attributed"] != base_restorable:
            baseline_validated = False
            validation_error = (
                f"DISPUTED_FIRST total attributed ({disp_first['total_scenario_attributed']}) "
                f"mismatches baseline ({base_restorable})"
            )

        for v in baseline_attribution.get("victims", []):
            vid = v.get("complaint_id")
            expected_amt = v.get("restorable_amount")
            if vid and expected_amt is not None:
                sim_amt = disp_first["scenario_remaining_attributed"].get(vid)
                if sim_amt != expected_amt:
                    baseline_validated = False
                    validation_error = (
                        f"Victim {vid} attributed amount ({sim_amt}) mismatches baseline ({expected_amt})"
                    )
                    break

    summary = (
        f"Sensitivity analysis completed for 3 debit-consumption assumptions. "
        f"Baseline agreement validated: {baseline_validated}."
    )
    if validation_error:
        summary += f" Validation note: {validation_error}."

    return {
        "case_id": case_id,
        "baseline_validated": baseline_validated,
        "validation_error": validation_error,
        "disclaimer": DISCLAIMER,
        "scenarios": scenarios,
        "summary": summary,
    }
