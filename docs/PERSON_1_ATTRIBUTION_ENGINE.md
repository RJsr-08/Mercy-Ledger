# PERSON 1 — SYNTHETIC CASE SIMULATOR

**Your deliverable is only `simulator.py`.** The team lead has implemented `attribution.py`, and `python check_my_work.py attribution` currently passes. Do not regenerate, replace or edit `attribution.py`.

## Your job

Build `generate_cases(n, seed) -> list[case]` in `simulator.py`. It creates deterministic synthetic cases for testing the Mercy Ledger pipeline. It must not claim to model real-world fraud rates or establish legal outcomes.

## Step 0 — Set-up

1. Install Python 3.11+.
2. Open a terminal inside the `mercy_ledger` project folder.
3. Run `python check_my_work.py attribution`. This should say PASS.
4. Run `python check_my_work.py simulator`. This should say FAIL while `simulator.py` is still a stub.

## Step 1 — Copy this prompt to your coding AI

Read `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md`, this file, `presets.py`, and the relevant golden case fixtures. Implement the COMPLETE `simulator.py` file only. Do not modify other files or expected outputs.

Requirements:

- Implement `generate_cases(n, seed) -> list[case]`.
- Use `random.Random(seed)` only; do not use global random state.
- Exactly `n` cases. Identical `(n, seed)` inputs must produce identical outputs, while a different seed should normally produce different cases.
- Use unique IDs such as `SIM_000` and set `tier` to `3`.
- Include every key in the CASE contract in `01_DATA_CONTRACT.md`.
- Represent all money as strings with exactly two decimal places.
- Transactions must be chronologically ordered and account balances must never become negative.
- Every complaint's `disputed_utr` must match exactly one CREDIT transaction, that credit must be at least the disputed amount, and the complaint timestamp must be after the credit.
- Complaint IDs must be unique within each case.
- Use a mix of cases: roughly one in four should be merchant-like, with `account_type` `CURRENT`, opening balance between `100000.00` and `600000.00`, and one small complaint (e.g. `200.00`). Other cases should have 2–6 victims, lower opening balances and some partial debit scenarios.
- `demo_today` must be a valid fixed date generated deterministically; do not read the system clock.
- `sla_context` must contain all five contract keys (null is allowed). `invoices` must be `[]`.
- `seizure_timestamp` should be later than the last transaction in generated cases.
- Do not use network calls, AI calls, files, or additional packages.

Return the complete `simulator.py` in one code block. Do not change `attribution.py`, the golden files, the checker, the shared data contract or another person's files.

## Step 2 — Run checks

Run:

```bash
python check_my_work.py simulator
```

If it fails, pass the checker's exact PROBLEMS list to your AI and ask it to fix only those points. When it says PASS, also run:

```bash
python check_my_work.py attribution
```

Both checks should pass. Send the integrator **only `simulator.py`**.

## What to tell judges

The simulator creates seeded synthetic cases to stress-test software behavior. It is not trained on real bank data, does not estimate actual fraud rates, and is not evidence that the rules perform accurately in production.
