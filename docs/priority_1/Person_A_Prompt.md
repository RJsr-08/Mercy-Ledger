# COPY/PASTE PROMPT — PERSON A, PRIORITY 1

You are **Person A — Simulator Owner** on the Mercy Ledger four-person hackathon team. I am providing the Mercy Ledger project folder. Inspect the actual files before writing code.

## Required reading

Read these files fully:
- `00_RULES_FOR_EVERY_AI.md`
- `01_DATA_CONTRACT.md`
- `PERSON_1_ATTRIBUTION_ENGINE.md`
- `presets.py`
- The relevant `golden/*.case.json` fixtures
- `check_my_work.py`

## Your only Priority 1 deliverable

Implement **`simulator.py` only**, with the exact interface:

`generate_cases(n, seed) -> list[case]`

The requirements in `PERSON_1_ATTRIBUTION_ENGINE.md` and `01_DATA_CONTRACT.md` are authoritative. Use `random.Random(seed)` only. Generate deterministic synthetic cases with complete schema, valid ISO timestamps, unique IDs, non-negative account balances, and complaint UTRs matching exactly one eligible CREDIT transaction. All money must be strings with two decimal places. No network, external libraries, system clock, file writes or AI calls in the product code.

## Do not do these things

- **Do not edit `attribution.py`.** It is already implemented and is the protected baseline.
- Do not edit `presets.py`, `pipeline.py`, `app.py`, the shared data contract, checkers or `golden/` files.
- Do not add the later chain-tracing, sensitivity, audit-hash or UI features in Priority 1.
- Do not return partial code, TODOs or a snippet.

## Test and handoff

Run:

```bash
python check_my_work.py simulator
python check_my_work.py attribution
```

If the simulator check fails, fix the actual problem without changing the checker or golden files. If it still fails after three focused attempts, stop and return the exact error output to Person D.

Return the **complete `simulator.py` file**, the exact commands run and their actual results. Send only `simulator.py` as the code deliverable. Never claim a check passed unless you ran it.
