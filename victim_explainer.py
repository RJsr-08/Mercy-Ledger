"""Plain-language victim explanation generator for Mercy Ledger.

Produces neutral, deterministic explanations of fund attribution and downstream
debit allocations per victim, without assuming guilt or claiming verified fund restoration.
"""
from decimal import Decimal

CENT = Decimal("0.01")

DISCLAIMER = (
    "Plain-language summary of mathematical model attribution only. This is not a legal "
    "finding, judicial order, or determination of fund recovery. Restoration decisions require "
    "formal authorization by the Investigating Officer under relevant procedural law."
)


def _format_inr(val):
    return f"\u20b9{val}"


def explain_victims(case, attribution):
    """Generate deterministic, neutral victim explanations based on attribution output.

    Args:
        case: dict containing case data.
        attribution: dict containing attribution output.

    Returns:
        dict with case_id, explanations (list), and disclaimer.
    """
    case_id = case.get("case_id", "UNKNOWN")
    victims = attribution.get("victims", [])
    explanations = []

    for v in victims:
        cid = v.get("complaint_id", "UNKNOWN")
        label = v.get("victim_label", f"Victim {cid}")
        disputed = v.get("disputed_amount", "0.00")
        method = v.get("attribution_method", "UNKNOWN")
        held = v.get("hold_in_current_account", v.get("restorable_amount", "0.00"))
        restorable = v.get("restorable_amount", held)
        fwd = v.get("forwarded_downstream", "0.00")
        fwd_traces = v.get("forwarded_trace", [])

        held_dec = Decimal(str(held))
        fwd_dec = Decimal(str(fwd))
        disputed_dec = Decimal(str(disputed))

        # Build neutral plain explanation
        parts = []
        if method == "INTACT":
            parts.append(
                f"The reported disputed amount of {_format_inr(disputed)} was received into the account "
                f"and remained fully intact with no intervening debit deductions. "
                f"The model calculates {_format_inr(restorable)} as remaining-attributed in this account "
                f"under the configured rules; this is not a decision to release funds."
            )
        elif held_dec > 0 and fwd_dec > 0:
            method_desc = "pro-rata allocation across commingled deposits" if method == "PRO_RATA" else "direct debit allocation"
            parts.append(
                f"Out of the disputed deposit of {_format_inr(disputed)}, {_format_inr(fwd)} was allocated to "
                f"subsequent outgoing debit transaction(s) via {method_desc}. "
                f"The model calculates {_format_inr(restorable)} as remaining-attributed in this account "
                f"under the configured rules; this is not a decision to release funds."
            )
        elif held_dec > 0 and fwd_dec == 0:
            parts.append(
                f"The full disputed deposit of {_format_inr(disputed)} remains present in the account. "
                f"The model calculates {_format_inr(restorable)} as remaining-attributed in this account "
                f"under the configured rules; this is not a decision to release funds."
            )
        else:  # held_dec == 0
            method_desc = "pro-rata distribution" if method == "PRO_RATA" else "direct debit assignment"
            parts.append(
                f"The entire disputed amount of {_format_inr(disputed)} is allocated to outgoing debit "
                f"transactions via {method_desc}. The model currently reports no amount remaining "
                f"attributable in this account under this scenario."
            )

        # Build specific limitation note
        if fwd_dec > 0:
            txn_refs = [t.get("debit_txn_id", "debit") for t in fwd_traces if t.get("debit_txn_id")]
            txn_str = f" ({', '.join(txn_refs)})" if txn_refs else ""
            limitation = (
                f"An amount of {_format_inr(fwd)} is assigned to outgoing debit(s){txn_str}. "
                f"The destination account is not verified by this single-account record, and "
                f"this model does not establish multi-hop recipient identity."
            )
        else:
            limitation = (
                "Attribution reflects single-account statement chronology under taint-first assumptions. "
                "Release of funds requires formal authorization by the Investigating Officer."
            )

        explanations.append({
            "complaint_id": cid,
            "victim_label": label,
            "reported_disputed_amount": disputed,
            "attribution_method": method,
            "restorable_amount": restorable,
            "forwarded_downstream": fwd,
            "plain_explanation": " ".join(parts),
            "limitation": limitation,
        })

    return {
        "case_id": case_id,
        "explanations": explanations,
        "disclaimer": DISCLAIMER,
    }
