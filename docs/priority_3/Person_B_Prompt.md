# COPY/PASTE PROMPT — PERSON B, PRIORITY 3

You are **Person B — Attribution Assumption Sensitivity Owner**. Only start after Priority 1 and 2 pass. Read `attribution.py`, `01_DATA_CONTRACT.md`, the existing assumptions field in attribution output, and the selected goldens. Do not change the existing engine.

## Create only

- `sensitivity.py`
- `test_priority3_sensitivity.py`

## Goal

Expose how the output of a controlled accounting model could change under explicit alternative debit-consumption assumptions. This is a sensitivity tool, **not an alternative legal rule, official SOP policy, or legal “restorable amount” calculator**.

Implement `analyze_sensitivity(case, baseline_attribution=None) -> dict` with named scenarios at minimum:
- `DISPUTED_FIRST`: consumes attributed/disputed pools before clean balance, distributing across victim pools according to the documented model where required.
- `CLEAN_FIRST`: consumes clean balance before the disputed pools.
- `PROPORTIONAL`: consumes clean and disputed balances proportionally to their available shares.

The returned object must identify each scenario's rule, remaining clean amount, remaining attributed per victim, total scenario-attributed amount, limitations and any errors. Use `scenario_remaining_attributed` labels; don't call a scenario amount money legally recoverable or legally due to a victim.

Important: inspect the existing attribution engine and avoid an unreviewable duplicate implementation. If you implement a separate simplified simulation, document every simplifying assumption and do not present it as equivalent to the full engine. Test the baseline scenario against selected golden outputs. If it cannot match the baseline on the supported examples, return a clear validation failure and advise that the feature not be shown; do not change `attribution.py` or golden files to force agreement.

Use `Decimal`, deterministic ordering, standard library only; never use system time, random data or network calls. Do not mutate inputs.

## Tests

Use `unittest` to test all three scenarios on a simple controlled case, conservation/reconciliation, deterministic results, missing input and baseline agreement checks on the supported SOP examples. Test that labels and disclaimers explicitly identify alternative assumptions.

## Handoff

Run `python -m unittest test_priority3_sensitivity.py`. Return the complete module, test, actual output and limitations. If accurate sensitivity would require refactoring the protected core engine, report the blocker rather than modifying it.
