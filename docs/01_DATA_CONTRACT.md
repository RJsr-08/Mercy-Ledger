# 01 — DATA CONTRACT (shared interface; do not change without integrator approval)

Money is a string with exactly two decimals, e.g. `"58000.00"`. Timestamps are ISO text such as `"2024-12-15T13:02:00"` (no timezone). Dates are `"2024-12-15"`. JSON `null` maps to Python `None`.

## 1. Case input

`presets.py` contains three preloaded demo cases: two scenarios derived from official Annexure-V illustrations and one explicitly illustrative merchant scenario. These are not three verified real-world cases.

```python
case = {
  "case_id": "SOP_ILL_1", "tier": 1|2|3, "title": str, "description": str,
  "demo_today": "YYYY-MM-DD",
  "account": {"account_id": str, "account_type": "SAVINGS"|"CURRENT"|"NODAL"|"POOL"|"ESCROW", "layer": int, "holder_name": str},
  "opening_balance": "873.00",
  "transactions": [{"txn_id", "timestamp", "type": "CREDIT"|"DEBIT", "amount", "utr", "narration"}, ...],
  "complaints": [{"complaint_id", "victim_label", "state", "disputed_utr", "disputed_amount", "complaint_timestamp"}, ...],
  "seizure_timestamp": "..." | None,
  "sla_context": {"account_holder_complaint_on", "grievance_filed_on", "io_decision_on", "io_direction_on", "suspension_started_on"},
  "invoices": [{"invoice_id", "date", "amount", "gstin", "claimed_utr"}, ...]
}
```

- A credit is treated as disputed only to the extent matched by a complaint's UTR; any excess is treated as clean for this demo model.
- The opening balance is assumed clean by this demo model. That assumption is not proof of provenance; the necessary statement history must be available for real analysis.
- Transaction rows are expected to be chronologically sortable. Attribution must use a stable timestamp sort and validate invalid or ambiguous input.
- **Assumption, not an SOP rule:** debits consume disputed balances before clean balances. This assumption is visible in output and is consistent with the two worked scenarios, but the SOP does not prescribe a universal debit-ordering algorithm.
- `forwarded_downstream` means a disputed amount allocated to an outgoing debit in the current account, with that debit's identifiers recorded. The current schema does **not** identify the receiving account, so it cannot prove the next hop or support verified multi-account tracing.

## 2. Module interfaces

| File | Owner in four-person plan | Function | Returns |
|---|---|---|---|
| `attribution.py` | Team lead (implemented; change only with approval) | `analyze_attribution(case)` | ATTRIBUTION dict |
| `simulator.py` | Teammate A | `generate_cases(n, seed)` | list of CASE dicts |
| `triage.py` | Teammate B | `triage(case, attribution, grievance=None)` | TRIAGE dict |
| `sla.py` | Teammate B | `compute_sla(case, as_of)` | list of 5 CLOCK dicts |
| `impact.py` | Teammate B | `case_impact(case, attribution, triage)` and `aggregate_impact(items)` | IMPACT / AGGREGATE dicts |
| `grievance.py` | Teammate C | `verify_grievance(case)` | GRIEVANCE dict |
| `orders.py` | Teammate C | `build_orders(case, attribution, triage, sla, grievance)` | dict containing 3 draft HTML documents |

The team lead owns integration, API schemas, UI wiring and end-to-end tests. `pipeline.py` calls attribution → grievance → triage → SLA → impact → orders. The `as_of` argument must be a date string; there is no system-clock fallback.

## 3. API shape

`POST /api/analyze-case` returns case metadata and these sections: `attribution`, `triage`, `sla`, `grievance`, `impact`, `orders`, `errors`. A section may be null when upstream processing fails; any non-empty `errors` array must be visible to the operator.

`GET /api/presets` returns preset metadata. `GET /api/portfolio-impact` returns `{ "aggregate": AGGREGATE, "errors": [...] }`.

The precise key shapes are defined by the corresponding `golden/*.json` files. Those expected outputs must be reviewed whenever a legal reference, assumption or interface is intentionally changed. Do not treat a cached response from the placeholder modules as evidence that real computation is working.

## 4. Output key groups

**ATTRIBUTION**: `case_id, opening_balance, closing_balance, balance_at_seizure, epochs, holds_sequence, victims, clean_ring_fenced, metrics, totals, assumptions, warnings`.

Each epoch includes `epoch_no, txn_id, timestamp, event_type, event_amount, event_utr, tainted_pool, clean_balance, ledger_balance, note`. Each victim includes `complaint_id, victim_label, disputed_utr, disputed_amount, attribution_method, hold_in_current_account, restorable_amount, forwarded_downstream, forwarded_trace, retention_ratio, sop_hold_amount`. Downstream trace rows contain the outgoing debit reference; they do not establish a receiving account unless that relationship is present in input data.

**TRIAGE**: `case_id, recommendation, rationale, score, thresholds, metrics, factors, citations, human_signoff_required, disclaimer`. The recommendation enum is `TARGETED_LIEN_ONLY`, `DIGITAL_SUSPENSION_PENDING_EDD`, or `SEIZURE_S106`.

**SLA**: Five clocks in this order: `BANK_GRIEVANCE_7D, IO_DECISION_15D, INTERIM_CUSTODY_15D, HOLD_REVIEW_90D, SUSPENSION_REVIEW_45D`. Each includes `key, label, sop_reference, starts_on, deadline, days_left, status, note`. Status values: `NOT_STARTED, ON_TRACK, DUE_SOON, OVERDUE, COMPLETED`.

**GRIEVANCE**: `case_id, results, disputed_total, disputed_matched, all_disputed_matched, disclaimer`. Each result includes the invoice match checks, verdict and reasons.

**IMPACT**: `case_id, title, recommendation, blanket_total_locked, blanket_innocent_locked, mercy_innocent_locked, innocent_capital_freed, victim_recoverable_preserved, victim_recoverable_in_blanket`.

Impact metrics must use the same reference timestamp (the seizure timestamp when supplied; otherwise the selected closing snapshot). A digital-services suspension is not the same as a cash lien: `mercy_innocent_locked` measures cash balance restricted by the recommended cash restraint, **not** lost access to digital payment channels. Under the demo metric, set cash locked to zero for a targeted lien or digital-only suspension; for a seizure recommendation, use the clean balance at the reference timestamp. State this interpretation in the UI/report.

**AGGREGATE**: `cases, blanket_innocent_locked, mercy_innocent_locked, innocent_capital_freed, reduction_percent, victim_recoverable_preserved, victim_recoverable_in_blanket, victim_funds_preserved_percent, by_recommendation, per_case`.

**ORDERS**: exactly `restoration_order_html`, `indemnity_bond_html`, and `edd_packet_html`. Each must be a complete HTML draft, visibly marked DRAFT, escaped against untrusted text, and require authorized officer review. These are not legally validated or court-ready documents.

## 5. SOP references and clock semantics

Use the supplied MHA/I4C SOP dated 2 January 2026 (`references/SOP_NCRP_CFCFRMS_2026-01-02.pdf`) as the primary source. Key sections:

- **Para 5(xiii)(a)/(b) and Annexure-V:** attribute to a victim where reasonably possible; use equitable/pro-rata distribution when commingling prevents attribution.
- **Para 5(ix):** unwarranted freezing orders are discouraged.
- **Para 5(viii):** the IO may verify with the account holder and allow an explanation before an order under Section 106(3) BNSS.
- **Para 9.1(i), (iii), (vi):** measures depend on the reported account, lawful LEA directions, repeated reports, EDD, and special treatment for nodal/pool/escrow accounts.
- **7-day grievance submission:** bank submission windows in Paras 10.1(a) and 10.2(b), triggered by the affected person's complaint.
- **15-day IO decision windows:** relevant grievance procedures in Paras 10.1(d)/(e) and 10.2(d)/(e), measured from the triggering grievance event specified by the relevant clause.
- **15-day interim custody completion:** Process 1(v) for the single-victim process and Process 2(h) for the multiple-victim process, following receipt of the IO/police direction.
- **Conditional 90-day hold-review/removal workflow:** Para 10.1's 90-day paragraph is measured from the grievance being submitted by the bank, applies to the described contested-hold circumstances, requires advance intimation and has exceptions and possible extension. Do not describe it as an automatic expiry for every hold.
- **45-day checkpoint:** this is a project-proposed review parameter, **not a general 45-day cap in the supplied SOP**. Always label it `PROPOSED POLICY - NOT an SOP clause`.

The rules-based triage thresholds and score are project-defined demonstration parameters, not an official MHA/I4C scorecard, not validated on real bank outcomes and not a finding of guilt. Every recommendation is decision support; an authorized officer retains the decision.

## 6. Dataset provenance notes

- `SOP_ILL_1` is derived from Annexure-V Illustration 1. The printed complaint date for Victim C appears as 16.12.2025 even though the transaction sequence is dated 15.12.2024; the demo fixture normalizes that complaint year to 2024 so the sequence is internally coherent. Document this normalization rather than claiming a verbatim reproduction.
- `SOP_ILL_2` is derived from Annexure-V Illustration 2. Any extra times added for the demo are assumptions to preserve the stated order, not source facts.
- `MERCHANT_200` is a wholly illustrative reconstruction. Names, UTRs, dates and details are invented; it is **not** attributed to any verified court case.
- Synthetic cases are for software stress testing only and do not demonstrate real-world fraud rates, classifier accuracy or legal outcomes.
