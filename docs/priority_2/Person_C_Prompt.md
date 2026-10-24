# COPY/PASTE PROMPT — PERSON C, PRIORITY 2

You are **Person C — Plain-Language Victim Explanation Owner**. Priority 1 has passed. Inspect `01_DATA_CONTRACT.md`, `attribution.py`, `PERSON_3_GRIEVANCE_AND_ORDERS.md`, and the relevant attribution fixtures first.

## Create only these new files

- `victim_explainer.py`
- `test_priority2_explainer.py`

Do not change `orders.py`, `grievance.py`, app.py, pipeline.py, the data contract, presets, checkers or golden files.

## Interface

Implement:

`explain_victims(case, attribution) -> dict`

Return JSON-safe data containing `case_id`, `explanations` (one entry for each attribution victim, preserving victim order), and `disclaimer`. Each entry should include complaint ID, victim label, reported disputed amount, method, currently attributed/restorable amount in this account, amount assigned to outgoing debits, a plain-language explanation and explicit limitation.

Use neutral, fixed templates, not generative text. Examples of wording principles:
- “The model calculates ₹X as remaining-attributed in this account under the configured rules; this is not a decision to release funds.”
- If an amount is forwarded, say it is assigned to an outgoing debit and the destination account is not verified unless the input explicitly establishes it.
- If restorable amount is zero, do not say the victim cannot ever recover money. Say the model currently reports no amount remaining attributable in this account under this scenario.
- Never claim funds have been recovered/restored unless verified restoration status is explicitly provided by the input. The current baseline schema may not contain that field, so normally do not claim restoration.

Preserve money as strings with two decimals and use `Decimal` only if you need to validate or compare. Use no LLM, network, external packages, system clock, or untrusted HTML. Keep output deterministic.

## Tests

Write `test_priority2_explainer.py` using `unittest`; test a victim with funds remaining, one with outgoing funds and zero remaining, multiple victims, deterministic repeat output, and absence of unsupported recovery/guilt claims.

## Handoff

Run:

```bash
python -m unittest test_priority2_explainer.py
python check_my_work.py all
```

Report the actual outcomes. Send Person D only `victim_explainer.py`, `test_priority2_explainer.py`, and the command results.
