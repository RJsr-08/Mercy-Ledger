# COPY/PASTE FOLLOW-UP PROMPT — PERSON D, PRIORITY 1 INTEGRATION

You are Person D, Mercy Ledger's integrator. I have now received complete files from Persons A, B and C. Work in the master project folder opened in this AI workspace. Do not begin Priority 2 yet.

## First inspect

Read `INTEGRATION_PROTOCOL.md` in this pack (if included in the workspace), `README_START_HERE.md`, `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md`, `app.py`, `pipeline.py`, `check_my_work.py`, and inspect `git diff` or file timestamps if available. Confirm the handed-off files correspond to the assigned roles.

## Merge only these Priority 1 deliverables

- A: `simulator.py`
- B: `triage.py`, `sla.py`, `impact.py`
- C: `grievance.py`, `orders.py`
- D: your `static/index.html`

Copy only those files. Preserve `attribution.py`, `presets.py`, `pipeline.py`, `app.py`, the data contract, checker, and golden files unless a specific integration issue requires an approved, minimal change. Do not silently change interfaces to make integration easier.

## Verify

Run the module checks and:

```bash
python check_my_work.py all
```

If a check fails, find the true mismatch between implementation, contract and golden result. Ask the relevant module AI to fix its file if needed. Never change a checker or golden output merely to force PASS.

Only after `check_my_work.py all` passes, run `python make_sample_data.py`, start the app with `python -m uvicorn app:app --host 127.0.0.1 --port 8000`, and manually test the full path through all existing presets and the offline fallback. Confirm the browser displays live backend results, not hardcoded answers.

Do not start Priority 2 until every core check passes and the main demonstration can be completed reliably. Return a short merge report listing files merged, commands run, actual outputs, remaining issues and whether the gate passed.
