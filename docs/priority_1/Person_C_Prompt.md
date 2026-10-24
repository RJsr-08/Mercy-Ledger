# COPY/PASTE PROMPT — PERSON C, PRIORITY 1

You are **Person C — Merchant Evidence and Draft Documents Owner** on the Mercy Ledger four-person hackathon team. Inspect the actual files before coding.

## Required reading

Read fully:
- `00_RULES_FOR_EVERY_AI.md`
- `01_DATA_CONTRACT.md`
- `PERSON_3_GRIEVANCE_AND_ORDERS.md`
- Relevant golden fixtures for `SOP_ILL_1`, `SOP_ILL_2`, `MERCHANT_200`, `EXTRA_INVOICE_BAD`, `EXTRA_INJECTION`, and `EXTRA_ESCROW`
- `check_my_work.py`
- The supplied SOP clauses cited by your role document

## Your only Priority 1 deliverables

Implement the complete files:
- `grievance.py`
- `orders.py`

Follow your role document's interfaces, expected strings and golden outputs. Invoice matching must be described as a **document-to-ledger consistency check**, not proof of innocence. GSTIN validation is format-only unless a registry lookup is explicitly supplied (it is not in this prototype). All generated documents must be marked DRAFT and reviewed by an authorized human. Escape all input-derived HTML text. The order generator must not calculate new money amounts; it may only present amounts already computed by the deterministic engine.

Use the standard library only in module code, and use `Decimal` if an amount must be formatted. Do not add external dependencies, external links, JavaScript or scripts to the generated order HTML.

## Do not

- Edit `attribution.py`, `triage.py`, `sla.py`, `impact.py`, `presets.py`, `pipeline.py`, `app.py`, the checker or golden files.
- Add the Priority 2/3 features yet.
- Claim the generated documents are legally operative or court-ready.

## Test and handoff

Run:

```bash
python check_my_work.py grievance
python check_my_work.py orders
```

If failures remain after three focused attempts, send Person D the actual error list rather than editing other files.

Return both **complete files** and the exact command output. Send only `grievance.py` and `orders.py` as code deliverables.
