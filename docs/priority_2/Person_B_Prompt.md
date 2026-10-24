# COPY/PASTE PROMPT — PERSON B, PRIORITY 2

You are **Person B — Review Flags Owner**. Priority 1 is passing. Work in a separate copy and inspect `01_DATA_CONTRACT.md`, `attribution.py`, `triage.py`, `impact.py`, `grievance.py`, `presets.py`, and `golden/SOP_ILL_1.attribution.json` before coding.

## Create only these new files

- `review_flags.py`
- `test_priority2_review_flags.py`

Do not edit existing modules, app.py, pipeline.py, presets, checker, shared contract or golden files.

## Interface

Implement:

`build_review_flags(case, attribution, grievance=None) -> dict`

Return JSON-safe data with `case_id`, `flags` (list), `count`, and a brief `summary`. Each flag must contain stable `code`, `severity`, `title`, `explanation`, and relevant transaction/complaint identifiers when known. The exact fields may be compact but must be consistent and documented in a module docstring.

At minimum implement these evidence-grounded flags:

1. **HOLD_ATTRIBUTION_GAP** — trigger when `sop_complaint_order_hold_total` and `mercy_right_sized_hold_total` differ. State both figures and explain that the discrepancy requires review. Do NOT say the current hold is unlawful or that one figure is automatically the legal answer.
2. **OUTFLOW_DESTINATION_UNVERIFIED** — trigger when a victim's `forwarded_trace` contains an outgoing debit but the source case schema provides no verified receiving-account link for it. Explain that the money left the current account but the next hop is not established by this single-account record.
3. **MULTIPLE_CLAIMS_REVIEW** — when multiple victim complaints relate to the case, ask the reviewer to verify the allocation and any competing claims. Do not assert the claims overlap unless the input supports that conclusion.
4. **EVIDENCE_NOT_COMPLETE** — only when `grievance` is provided and its fields show one or more complaints have missing or unmatched evidence. Explain the exact missing/mismatched status.

Do not flag an account holder as guilty or innocent. Do not call the `triage` score an official legal score. Use `Decimal` if comparing amounts; return money as strings. Be deterministic and don't mutate inputs.

## Tests

Write `test_priority2_review_flags.py` with `unittest`. Cover at least: a hold/attribution gap, an outgoing transaction without destination linkage, a case with no gap, and a multi-claim case. Assert wording does not call a hold unlawful or a holder criminal.

## Handoff

Run:

```bash
python -m unittest test_priority2_review_flags.py
python check_my_work.py all
```

The full check in your separate copy is expected to pass only if it was already fully integrated; report the actual result rather than assuming. Send Person D only `review_flags.py`, `test_priority2_review_flags.py`, and the actual test output.
