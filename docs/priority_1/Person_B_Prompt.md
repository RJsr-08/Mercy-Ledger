# COPY/PASTE PROMPT — PERSON B, PRIORITY 1

You are **Person B — Triage, Deadline and Impact Owner** on the Mercy Ledger four-person hackathon team. Inspect the provided project before coding.

## Required reading

Read completely:
- `00_RULES_FOR_EVERY_AI.md`
- `01_DATA_CONTRACT.md`
- `PERSON_2_TRIAGE_SLA_IMPACT.md`
- `presets.py`
- The relevant golden fixtures: `SOP_ILL_1`, `SOP_ILL_2`, `MERCHANT_200`, `EXTRA_MIXED`, `EXTRA_ESCROW`, `EXTRA_INVOICE_BAD`, and `PRESETS.aggregate_impact.json`
- `check_my_work.py`

## Your only Priority 1 deliverables

Implement these three complete files, preserving every signature and JSON key in the shared contract:
- `triage.py`
- `sla.py`
- `impact.py`

Follow `PERSON_2_TRIAGE_SLA_IMPACT.md` and golden expected outputs exactly unless you find a material conflict with the shared contract or supplied SOP. If you do, stop and explain the conflict instead of guessing.

Important constraints:
- Triage weights and thresholds are a **project-defined illustrative scorecard**, not official SOP scoring and not a validated real-world fraud classifier.
- Use `Decimal`, never float, for money.
- Use only the supplied `as_of` date; do not use the system clock.
- The 45-day suspension review is a proposed project checkpoint, not an SOP deadline. Use the exact required label.
- A digital-services suspension is not the same as cash being held. Do not overstate what the impact metric measures.
- Never change `attribution.py`, `presets.py`, `pipeline.py`, `app.py`, the checker or golden files.
- Do not implement stretch features during Priority 1.

## Test and handoff

Run:

```bash
python check_my_work.py triage
python check_my_work.py sla
python check_my_work.py impact
```

Fix actual failures only. If the golden, contract or SOP appears inconsistent, send the exact conflict to Person D; don't silently edit the expected outputs.

Return the **complete files `triage.py`, `sla.py`, and `impact.py`**, and report the actual command outputs. Send only those three code files to Person D.
