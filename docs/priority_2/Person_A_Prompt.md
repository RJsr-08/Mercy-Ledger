# COPY/PASTE PROMPT — PERSON A, PRIORITY 2

You are **Person A — Financial Invariants and Stress-Test Owner**. Priority 1 has passed. Work in a separate copy of the passing Mercy Ledger project. Read `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md`, `attribution.py`, `simulator.py`, `pipeline.py`, and the existing golden case/attribution files first.

## Create only these new files

1. `invariants.py`
2. `stress_test.py`
3. `test_priority2_invariants.py`

Do not edit or replace any existing project file.

## `invariants.py` contract

Implement:

`check_case_invariants(case, attribution) -> dict`

Return JSON-safe data with this shape:

```python
{
  "case_id": "...",
  "passed": True,
  "checks": [{"id": "...", "passed": True, "details": "..."}],
  "errors": []
}
```

At minimum check:
- In every attribution epoch, `ledger_balance == clean_balance + sum(tainted_pool.values())` using `Decimal`.
- All reported epoch balances, pool amounts, victim amounts and allocation totals are non-negative.
- For each victim, `hold_in_current_account + forwarded_downstream == disputed_amount` within exact cent precision where the existing data model promises this identity; if a real supported case violates it, report a failed check rather than rewriting attribution output.
- Sum of victim `restorable_amount` equals `totals.restorable_total`.
- Sum of victim `forwarded_downstream` equals `totals.forwarded_downstream_total`.
- Restorable total does not exceed `balance_at_seizure`.
- Closing balance agrees with the final ledger epoch (or opening balance if no transactions exist).

Use clear check IDs and diagnostic details. Do not infer next-hop accounts from `forwarded_trace`. If a comparison is not meaningful because required inputs are absent, return a failed or explicitly unavailable check with an explanation; never count unknown as passed. Do not mutate input dictionaries. Convert outputs to JSON-safe strings/bools/lists.

## `stress_test.py` contract

Implement:

`run_stress_test(n=40, seed=7) -> dict`

Use `simulator.generate_cases(n, seed)` and `attribution.analyze_attribution(case)`, then `check_case_invariants`. Report the number actually requested, generated, executed, passed, failed, seed and details for failing cases. No hardcoded success counts. Use deterministic inputs and no system clock or network. Keep runtime reasonable at n <= 200. Handle module exceptions as failures, not as passes.

## Tests

Write `test_priority2_invariants.py` using `unittest` and available presets. Include successful checks on real preset fixtures and a deliberately mutated attribution object that must fail at least one invariant. Test stress-test result counts from an actual small run. Do not edit `check_my_work.py`, existing tests or `golden/`.

## Handoff

Run:

```bash
python -m unittest test_priority2_invariants.py
python check_my_work.py attribution
python check_my_work.py simulator
```

Send Person D only the three new files plus the actual command outputs and known limitations. Do not claim these are real-world accuracy tests; they verify internal consistency on selected and synthetic cases.
