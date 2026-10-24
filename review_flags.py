"""Evidence-grounded review flags for Mercy Ledger.

Produces explicit review flags and explanatory context for investigating officers
and bank review personnel without declaring holds unlawful or presuming guilt.

Flag Schema:
{
    "case_id": str,
    "count": int,
    "summary": str,
    "flags": [
        {
            "code": str,             # e.g., "HOLD_ATTRIBUTION_GAP"
            "severity": str,         # "HIGH" | "MEDIUM" | "LOW" | "INFO"
            "title": str,            # Human-readable label
            "explanation": str,      # Detailed, objective explanation
            "complaint_ids": list,   # Associated complaint IDs (strings)
            "txn_ids": list,         # Associated transaction IDs (strings)
        },
        ...
    ]
}
"""
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def _money(val):
    if not isinstance(val, Decimal):
        val = Decimal(str(val))
    return format(val.quantize(CENT, rounding=ROUND_HALF_UP), ".2f")


def build_review_flags(case, attribution, grievance=None):
    """Build review flags for a case, attribution output, and optional grievance.

    Args:
        case: dict containing case data.
        attribution: dict containing attribution analysis output.
        grievance: optional dict containing grievance verification output.

    Returns:
        dict with case_id, count, summary, and list of flag dicts.
    """
    case_id = case.get("case_id", "UNKNOWN")
    flags = []

    complaints = case.get("complaints", [])
    complaint_ids = [c["complaint_id"] for c in complaints if "complaint_id" in c]
    transactions = case.get("transactions", [])

    # 1. HOLD_ATTRIBUTION_GAP
    # Trigger when sop_complaint_order_hold_total and mercy_right_sized_hold_total differ.
    totals = attribution.get("totals", {})
    sop_hold_str = totals.get("sop_complaint_order_hold_total")
    mercy_hold_str = totals.get("mercy_right_sized_hold_total")

    if sop_hold_str is not None and mercy_hold_str is not None:
        sop_hold = Decimal(str(sop_hold_str))
        mercy_hold = Decimal(str(mercy_hold_str))
        if sop_hold != mercy_hold:
            diff = abs(sop_hold - mercy_hold)
            flags.append({
                "code": "HOLD_ATTRIBUTION_GAP",
                "severity": "HIGH",
                "title": "Hold and Attribution Total Discrepancy",
                "explanation": (
                    f"Provisional complaint-order hold total ({_money(sop_hold)}) differs from "
                    f"right-sized attribution-derived hold total ({_money(mercy_hold)}) by "
                    f"{_money(diff)}. This discrepancy requires case officer review; neither "
                    f"figure is an automatic legal determination, and existing provisional holds "
                    f"remain in force pending authorized officer decision."
                ),
                "complaint_ids": list(complaint_ids),
                "txn_ids": [],
            })

    # 2. OUTFLOW_DESTINATION_UNVERIFIED
    # Trigger when a victim's forwarded_trace contains outgoing debits but the schema
    # provides no verified receiving-account link for it.
    victims = attribution.get("victims", [])
    outflow_txns = []
    outflow_complaints = []
    total_outflow = Decimal("0.00")

    for v in victims:
        traces = v.get("forwarded_trace", [])
        if traces:
            cid = v.get("complaint_id")
            if cid and cid not in outflow_complaints:
                outflow_complaints.append(cid)
            for t in traces:
                txn_id = t.get("debit_txn_id")
                if txn_id and txn_id not in outflow_txns:
                    outflow_txns.append(txn_id)
                amt_str = t.get("amount")
                if amt_str:
                    total_outflow += Decimal(str(amt_str))

    if outflow_txns:
        flags.append({
            "code": "OUTFLOW_DESTINATION_UNVERIFIED",
            "severity": "MEDIUM",
            "title": "Outflow Destination Unverified",
            "explanation": (
                f"Disputed funds totaling {_money(total_outflow)} were forwarded downstream via "
                f"outgoing debit transaction(s) ({', '.join(outflow_txns)}), but the single-account "
                f"record provides no verified receiving-account link. The funds left this account, "
                f"but the downstream destination is not established by the available statement data."
            ),
            "complaint_ids": outflow_complaints,
            "txn_ids": outflow_txns,
        })

    # 3. MULTIPLE_CLAIMS_REVIEW
    # Trigger when multiple victim complaints relate to the case.
    if len(complaints) > 1:
        disputed_utrs = {c.get("disputed_utr") for c in complaints if c.get("disputed_utr")}
        matched_txns = [
            t["txn_id"] for t in transactions
            if t.get("utr") in disputed_utrs and "txn_id" in t
        ]
        flags.append({
            "code": "MULTIPLE_CLAIMS_REVIEW",
            "severity": "INFO",
            "title": "Multiple Victim Claims Requiring Review",
            "explanation": (
                f"Case involves {len(complaints)} distinct victim complaints "
                f"({', '.join(complaint_ids)}). Reviewer should verify fund allocations across "
                f"claimants. This review prompt does not assert that claims overlap or conflict, "
                f"but prompts coordinated verification."
            ),
            "complaint_ids": list(complaint_ids),
            "txn_ids": matched_txns,
        })

    # 4. EVIDENCE_NOT_COMPLETE
    # Only when grievance is provided and shows missing or unmatched evidence.
    if grievance is not None and isinstance(grievance, dict):
        all_matched = grievance.get("all_disputed_matched", False)
        results = grievance.get("results", [])
        unmatched_details = []
        unmatched_cids = []

        for r in results:
            verdict = r.get("verdict")
            if verdict != "MATCHED":
                cid = r.get("complaint_id", "UNKNOWN")
                unmatched_cids.append(cid)
                reasons = r.get("reasons", [])
                reasons_str = "; ".join(reasons) if reasons else "documentation incomplete"
                unmatched_details.append(f"Complaint {cid} ({verdict}: {reasons_str})")

        if not all_matched or unmatched_cids:
            flags.append({
                "code": "EVIDENCE_NOT_COMPLETE",
                "severity": "HIGH",
                "title": "Incomplete or Unmatched Merchant Documentation",
                "explanation": (
                    f"Merchant grievance verification indicates incomplete or unmatched documentation "
                    f"for {len(unmatched_cids)} complaint(s): {', '.join(unmatched_details)}. "
                    f"Investigating Officer verification is required under SOP Para 10."
                ),
                "complaint_ids": unmatched_cids,
                "txn_ids": [],
            })

    count = len(flags)
    if count == 0:
        summary = "No review flags triggered for this case."
    elif count == 1:
        summary = f"1 review flag identified ({flags[0]['code']}) requiring officer attention."
    else:
        codes = ", ".join(f["code"] for f in flags)
        summary = f"{count} review flags identified ({codes}) requiring officer attention."

    return {
        "case_id": case_id,
        "count": count,
        "summary": summary,
        "flags": flags,
    }
