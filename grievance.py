"""
grievance.py  -  verify_grievance(case) -> GRIEVANCE dict
Owner: Person C  (Merchant Evidence and Draft Documents)

Purpose: check submitted merchant invoices for consistency against the ledger.
This is a document-to-ledger consistency check, NOT proof of a genuine sale.
The Investigating Officer verifies and decides under SOP Para 10.
Standard library only; no float arithmetic on money.
"""

import re
from datetime import date
from decimal import Decimal

# ── constants ────────────────────────────────────────────────────────────────

_DISCLAIMER = (
    "Consistency check of merchant documents against ledger rows. "
    "It does not prove the sale is genuine; the IO verifies under SOP Para 10."
)

# GSTIN regex (format only; no registry lookup is performed or available)
_GSTIN_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")


# ── helpers ──────────────────────────────────────────────────────────────────

def _parse_date(s):
    """Return a date object from an ISO date string YYYY-MM-DD."""
    return date.fromisoformat(s)


def _credit_date(transactions, utr):
    """Return the date part of the CREDIT transaction matching `utr`, or None."""
    for txn in transactions:
        if txn["type"] == "CREDIT" and txn["utr"] == utr:
            # timestamp is like "2026-09-01T10:15:00"
            return _parse_date(txn["timestamp"].split("T")[0])
    return None


def _abs_day_diff(d1, d2):
    """Absolute difference in calendar days between two date objects."""
    return abs((d1 - d2).days)


# ── public API ───────────────────────────────────────────────────────────────

def verify_grievance(case):
    """
    For each complaint in case["complaints"] (in list order):
      - find the first invoice whose claimed_utr == complaint disputed_utr
      - run four checks; derive verdict and reasons
    Returns GRIEVANCE dict matching the contract.
    """
    case_id = case["case_id"]
    transactions = case.get("transactions", [])
    invoices = case.get("invoices", [])
    complaints = case.get("complaints", [])

    # Build a lookup: claimed_utr -> first invoice with that UTR
    invoice_by_utr = {}
    for inv in invoices:
        utr = inv.get("claimed_utr")
        if utr and utr not in invoice_by_utr:
            invoice_by_utr[utr] = inv

    results = []

    for comp in complaints:
        disputed_utr = comp["disputed_utr"]
        complaint_id = comp["complaint_id"]
        disputed_amount = comp["disputed_amount"]

        inv = invoice_by_utr.get(disputed_utr)

        if inv is None:
            # No invoice submitted for this UTR
            result = {
                "checks": {
                    "amount_match": False,
                    "date_within_1_day": False,
                    "gstin_format_valid": False,
                    "utr_match": False,
                },
                "complaint_id": complaint_id,
                "disputed_amount": disputed_amount,
                "disputed_utr": disputed_utr,
                "invoice_id": None,
                "reasons": ["No invoice submitted for this disputed UTR."],
                "verdict": "NO_INVOICE",
            }
        else:
            # Invoice found; run checks
            utr_match = True  # by definition: we found it by UTR

            # amount_match: exact decimal equality
            try:
                amount_match = Decimal(inv["amount"]) == Decimal(disputed_amount)
            except Exception:
                amount_match = False

            # date_within_1_day: find credit transaction date
            credit_dt = _credit_date(transactions, disputed_utr)
            if credit_dt is None:
                date_within_1_day = False
            else:
                try:
                    inv_dt = _parse_date(inv["date"])
                    date_within_1_day = _abs_day_diff(inv_dt, credit_dt) <= 1
                except Exception:
                    date_within_1_day = False

            # gstin_format_valid: format only, no registry lookup
            gstin_raw = inv.get("gstin", "")
            gstin_format_valid = bool(_GSTIN_RE.match(str(gstin_raw)))

            # Build reasons list (in fixed order for failed checks)
            reasons = []
            if not amount_match:
                reasons.append("Invoice amount differs from disputed amount.")
            if not date_within_1_day:
                reasons.append("Invoice date is more than 1 day from the credit date.")
            if not gstin_format_valid:
                reasons.append(
                    "GSTIN is not in valid 15-character format "
                    "(format check only, no registry lookup)."
                )
            if not reasons:
                reasons = ["All checks passed."]

            # Verdict
            if amount_match and date_within_1_day and gstin_format_valid:
                verdict = "MATCHED"
            elif amount_match:
                verdict = "PARTIAL"
            else:
                verdict = "NOT_MATCHED"

            result = {
                "checks": {
                    "amount_match": amount_match,
                    "date_within_1_day": date_within_1_day,
                    "gstin_format_valid": gstin_format_valid,
                    "utr_match": utr_match,
                },
                "complaint_id": complaint_id,
                "disputed_amount": disputed_amount,
                "disputed_utr": disputed_utr,
                "invoice_id": inv["invoice_id"],
                "reasons": reasons,
                "verdict": verdict,
            }

        results.append(result)

    disputed_total = len(results)
    disputed_matched = sum(1 for r in results if r["verdict"] == "MATCHED")
    all_disputed_matched = (disputed_total > 0) and (disputed_matched == disputed_total)

    return {
        "all_disputed_matched": all_disputed_matched,
        "case_id": case_id,
        "disclaimer": _DISCLAIMER,
        "disputed_matched": disputed_matched,
        "disputed_total": disputed_total,
        "results": results,
    }
