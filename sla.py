"""SLA and statutory deadline tracking for Mercy Ledger.

Calculates calendar-day deadlines and progress tracking for bank grievance
filing, IO decision windows, interim custody, conditional hold reviews,
and proposed digital-suspension review checkpoints.
"""
from datetime import date, timedelta

CLOCKS_SPEC = [
    {
        "key": "BANK_GRIEVANCE_7D",
        "label": "Bank submits grievance (7 days)",
        "sop_reference": "SOP Para 10.1(a) / 10.2(b)",
        "start_key": "account_holder_complaint_on",
        "length_days": 7,
        "completed_key": "grievance_filed_on",
        "due_soon_days": 2,
        "note": None,
    },
    {
        "key": "IO_DECISION_15D",
        "label": "IO decides on grievance (15 days)",
        "sop_reference": "SOP Para 10.1(d)(e) / 10.2(d)(e)",
        "start_key": "grievance_filed_on",
        "length_days": 15,
        "completed_key": "io_decision_on",
        "due_soon_days": 3,
        "note": None,
    },
    {
        "key": "INTERIM_CUSTODY_15D",
        "label": "Bank completes interim custody (15 days from IO direction)",
        "sop_reference": "SOP Para 11, Process 1(v) (single victim) / Process 2(h) (multiple victims)",
        "start_key": "io_direction_on",
        "length_days": 15,
        "completed_key": None,
        "due_soon_days": 3,
        "note": "The applicable process depends on whether there is one victim or multiple competing victims.",
    },
    {
        "key": "HOLD_REVIEW_90D",
        "label": "Conditional hold-review/removal milestone (90 days from bank grievance submission)",
        "sop_reference": "SOP Para 10.1, conditional 90-day grievance/hold paragraph",
        "start_key": "grievance_filed_on",
        "length_days": 90,
        "completed_key": None,
        "due_soon_days": 15,
        "note": (
            "Not a universal automatic expiry. Check whether another case or court proceeding requires retention, "
            "whether lawful directions are pending, and whether an extension applies. Bank intimation is required at "
            "least 15 calendar days before the relevant 90-day point; an LEA may request up to 90 additional days."
        ),
    },
    {
        "key": "SUSPENSION_REVIEW_45D",
        "label": "Digital-suspension review checkpoint (45 days; proposed policy)",
        "sop_reference": "PROPOSED POLICY - NOT an SOP clause",
        "start_key": "suspension_started_on",
        "length_days": 45,
        "completed_key": None,
        "due_soon_days": 7,
        "note": "Project-defined review checkpoint only. The supplied SOP does not establish a general 45-day suspension cap.",
    },
]


def compute_sla(case, as_of):
    """Compute SLA deadline clocks relative to as_of date."""
    as_of_date = date.fromisoformat(as_of)
    sla_context = case.get("sla_context", {})

    clocks = []
    for spec in CLOCKS_SPEC:
        start_key = spec["start_key"]
        starts_on_str = sla_context.get(start_key)

        if not starts_on_str:
            clocks.append({
                "days_left": None,
                "deadline": None,
                "key": spec["key"],
                "label": spec["label"],
                "note": spec["note"],
                "sop_reference": spec["sop_reference"],
                "starts_on": None,
                "status": "NOT_STARTED",
            })
            continue

        start_date = date.fromisoformat(starts_on_str)
        deadline_date = start_date + timedelta(days=spec["length_days"])
        deadline_str = deadline_date.isoformat()

        completed_key = spec["completed_key"]
        is_completed = bool(completed_key and sla_context.get(completed_key))

        if is_completed:
            status = "COMPLETED"
            days_left = None
        else:
            days_left = (deadline_date - as_of_date).days
            if days_left < 0:
                status = "OVERDUE"
            elif days_left <= spec["due_soon_days"]:
                status = "DUE_SOON"
            else:
                status = "ON_TRACK"

        clocks.append({
            "days_left": days_left,
            "deadline": deadline_str,
            "key": spec["key"],
            "label": spec["label"],
            "note": spec["note"],
            "sop_reference": spec["sop_reference"],
            "starts_on": starts_on_str,
            "status": status,
        })

    return clocks
