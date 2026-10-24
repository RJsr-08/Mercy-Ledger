"""
presets.py  --  SHARED TEST DATA. OWNER: Integrator. NOBODY ELSE MAY EDIT THIS FILE.
Three demo cases. All money values are STRINGS (never floats).
"""

def _t(txn_id, ts, typ, amount, utr, narration=""):
    return {"txn_id": txn_id, "timestamp": ts, "type": typ, "amount": amount,
            "utr": utr, "narration": narration}

def _c(cid, label, utr, amount, ts, state="Not specified in SOP"):
    return {"complaint_id": cid, "victim_label": label, "state": state,
            "disputed_utr": utr, "disputed_amount": amount, "complaint_timestamp": ts}

PRESETS = {
    "SOP_ILL_1": {
        "case_id": "SOP_ILL_1",
        "tier": 1,
        "title": "SOP Annexure-V, Illustration 1 (Attribution possible)",
        "description": ("SOP-derived ledger from MHA/I4C SOP (2 Jan 2026), Annexure-V, Illustration 1, with the Victim C complaint year normalized for internal chronology. "
                        "A's and B's money has left the account; C's money is intact. "
                        "Complaint date of C is printed as 16.12.2025 in the SOP (typo) - we use 2024."),
        "demo_today": "2025-01-02",
        "account": {"account_id": "ACC-ILL1", "account_type": "SAVINGS", "layer": 1,
                    "holder_name": "Illustration-1 Account Holder"},
        "opening_balance": "873.00",
        "transactions": [
            _t("T1", "2024-12-15T13:02:00", "CREDIT", "97000.00", "UTR-ILL1-A", "Credit from Victim A"),
            _t("T2", "2024-12-15T13:09:00", "DEBIT",  "97000.00", "OUT-ILL1-001", "Outgoing transfer"),
            _t("T3", "2024-12-15T14:17:00", "CREDIT", "58000.00", "UTR-ILL1-B", "Credit from Victim B"),
            _t("T4", "2024-12-15T14:22:00", "DEBIT",  "50000.00", "OUT-ILL1-002", "Outgoing transfer"),
            _t("T5", "2024-12-15T15:11:00", "CREDIT", "150000.00", "UTR-ILL1-C", "Credit from Victim C"),
        ],
        "complaints": [
            _c("B", "Victim B", "UTR-ILL1-B", "58000.00",  "2024-12-16T14:30:00"),
            _c("A", "Victim A", "UTR-ILL1-A", "97000.00",  "2024-12-16T16:15:00"),
            _c("C", "Victim C", "UTR-ILL1-C", "150000.00", "2024-12-16T19:45:00"),
        ],
        "seizure_timestamp": "2024-12-15T16:00:00",
        "sla_context": {"account_holder_complaint_on": "2024-12-17", "grievance_filed_on": "2024-12-20",
                        "io_decision_on": None, "io_direction_on": None,
                        "suspension_started_on": "2024-12-15"},
        "invoices": [],
    },
    "SOP_ILL_2": {
        "case_id": "SOP_ILL_2",
        "tier": 1,
        "title": "SOP Annexure-V, Illustration 2 (Commingled - pro-rata)",
        "description": ("SOP-derived ledger from MHA/I4C SOP, Annexure-V, Illustration 2; any added clock times are documented demo assumptions. Five victims V,W,X,Y,Z commingled, "
                        "then a Rs 47,226 partial debit. The SOP gives only DATES of complaints; we assumed clock "
                        "times that preserve the SOP order X, V, Y, Z, W. Seizure time (15:30) is also assumed."),
        "demo_today": "2025-01-25",
        "account": {"account_id": "ACC-ILL2", "account_type": "SAVINGS", "layer": 1,
                    "holder_name": "Illustration-2 Account Holder"},
        "opening_balance": "0.00",
        "transactions": [
            _t("T1", "2024-12-15T12:20:00", "CREDIT", "85326.00", "UTR-ILL2-V", "Credit from V"),
            _t("T2", "2024-12-15T12:51:00", "CREDIT", "38443.00", "UTR-ILL2-W", "Credit from W"),
            _t("T3", "2024-12-15T13:23:00", "CREDIT", "50000.00", "UTR-ILL2-X", "Credit from X"),
            _t("T4", "2024-12-15T13:55:00", "CREDIT", "50000.00", "UTR-ILL2-Y", "Credit from Y"),
            _t("T5", "2024-12-15T14:30:00", "CREDIT", "30000.00", "UTR-ILL2-Z", "Credit from Z"),
            _t("T6", "2024-12-15T15:06:00", "DEBIT",  "47226.00", "OUT-ILL2-001", "Partial withdrawal"),
        ],
        "complaints": [
            _c("X", "Victim X", "UTR-ILL2-X", "50000.00", "2024-12-16T10:00:00"),
            _c("V", "Victim V", "UTR-ILL2-V", "85326.00", "2024-12-16T11:00:00"),
            _c("Y", "Victim Y", "UTR-ILL2-Y", "50000.00", "2024-12-17T09:00:00"),
            _c("Z", "Victim Z", "UTR-ILL2-Z", "30000.00", "2024-12-17T10:00:00"),
            _c("W", "Victim W", "UTR-ILL2-W", "38443.00", "2024-12-17T11:00:00"),
        ],
        "seizure_timestamp": "2024-12-15T15:30:00",
        "sla_context": {"account_holder_complaint_on": None, "grievance_filed_on": None,
                        "io_decision_on": None, "io_direction_on": None,
                        "suspension_started_on": "2024-12-15"},
        "invoices": [],
    },
    "MERCHANT_200": {
        "case_id": "MERCHANT_200",
        "tier": 2,
        "title": "Illustrative merchant Rs 200 scenario",
        "description": ("Invented demonstration scenario: a merchant account with Rs 4,85,000 of opening clean capital receives one disputed Rs 200 UPI payment for goods. All names, UTRs and dates are invented; this is not a representation of a verified court case."),
        "demo_today": "2026-09-10",
        "account": {"account_id": "ACC-MERCHANT", "account_type": "CURRENT", "layer": 3,
                    "holder_name": "Example Merchant"},
        "opening_balance": "485000.00",
        "transactions": [
            _t("T1", "2026-09-01T10:15:00", "CREDIT", "200.00", "UTR-MERCHANT-0200", "UPI payment for medicines"),
        ],
        "complaints": [
            _c("P1", "Complainant P1", "UTR-MERCHANT-0200", "200.00", "2026-09-01T16:40:00", "Bihar"),
        ],
        "seizure_timestamp": "2026-09-02T09:00:00",
        "sla_context": {"account_holder_complaint_on": "2026-09-01", "grievance_filed_on": None,
                        "io_decision_on": None, "io_direction_on": None,
                        "suspension_started_on": "2026-09-02"},
        "invoices": [
            {"invoice_id": "INV-MERCHANT-2026-0412", "date": "2026-09-01", "amount": "200.00",
             "gstin": "08ABCDE1234F1Z5", "claimed_utr": "UTR-MERCHANT-0200"},
        ],
    },
    "SEIZURE_EDGE_4V": {
        "case_id": "SEIZURE_EDGE_4V",
        "tier": 2,
        "title": "Illustrative four-victim seizure-time edge case",
        "description": (
            "Illustrative user-supplied ledger for exercising seizure-time, late-complaint, "
            "duplicate-looking narration, and one-paisa handling. The supplied credit amounts "
            "are used as the four distinct complaint amounts; the calendar date and complaint "
            "clock times are demo assumptions because they were not supplied."
        ),
        "demo_today": "2026-10-24",
        "account": {"account_id": "ACC-EDGE-4V", "account_type": "SAVINGS", "layer": 1,
                    "holder_name": "Illustrative Account Holder"},
        "opening_balance": "25000.00",
        "transactions": [
            _t("T1",  "2026-10-24T09:00:00", "CREDIT", "75000.00", "UTR-EDGE-CLEAN-01", "UPI transfer received"),
            _t("T2",  "2026-10-24T09:05:00", "CREDIT", "40000.00", "UTR-EDGE-A", "UPI transfer received"),
            _t("T3",  "2026-10-24T09:06:00", "CREDIT", "60000.00", "UTR-EDGE-B", "UPI transfer received"),
            _t("T4",  "2026-10-24T09:07:00", "CREDIT", "20000.00", "UTR-EDGE-C", "UPI transfer received"),
            _t("T5",  "2026-10-24T09:10:00", "DEBIT",  "50000.00", "OUT-EDGE-01", "Outgoing transfer"),
            _t("T6",  "2026-10-24T09:15:00", "DEBIT",  "30000.00", "OUT-EDGE-02", "Outgoing transfer"),
            _t("T7",  "2026-10-24T09:20:00", "CREDIT", "10000.00", "UTR-EDGE-CLEAN-02", "UPI transfer received"),
            _t("T8",  "2026-10-24T09:25:00", "DEBIT",  "100000.00", "OUT-EDGE-03", "Outgoing transfer"),
            _t("T9",  "2026-10-24T09:30:00", "CREDIT", "50000.00", "UTR-EDGE-D", "UPI transfer received"),
            _t("T10", "2026-10-24T09:35:00", "DEBIT",  "25000.00", "OUT-EDGE-04", "Outgoing transfer"),
            _t("T11", "2026-10-24T09:40:00", "DEBIT",  "1.00", "OUT-EDGE-05", "Outgoing transfer"),
            _t("T12", "2026-10-24T09:45:00", "CREDIT", "0.01", "UTR-EDGE-CLEAN-03", "UPI transfer received"),
        ],
        "complaints": [
            _c("A", "Victim A", "UTR-EDGE-A", "40000.00", "2026-10-24T09:21:00"),
            _c("B", "Victim B", "UTR-EDGE-B", "60000.00", "2026-10-24T09:22:00"),
            _c("C", "Victim C", "UTR-EDGE-C", "20000.00", "2026-10-24T09:23:00"),
            _c("D", "Victim D", "UTR-EDGE-D", "50000.00", "2026-10-24T09:50:00"),
        ],
        "seizure_timestamp": "2026-10-24T09:20:00",
        "sla_context": {"account_holder_complaint_on": None, "grievance_filed_on": None,
                        "io_decision_on": None, "io_direction_on": None,
                        "suspension_started_on": "2026-10-24"},
        "invoices": [],
    },
}

def list_presets():
    return [{"id": k, "title": v["title"], "tier": v["tier"], "description": v["description"]}
            for k, v in PRESETS.items()]

def get_preset(preset_id):
    return PRESETS[preset_id]
