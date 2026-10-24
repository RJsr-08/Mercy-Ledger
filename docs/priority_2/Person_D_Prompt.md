# COPY/PASTE PROMPT — PERSON D, PRIORITY 2 UI WORK

You are **Person D — Frontend Owner and Integrator**. Priority 1 is passed and frozen. Inspect the actual existing app, the current `static/index.html`, API schema, `attribution.epochs`, `impact`, `grievance`, `orders`, and this priority README before coding. Work in the master project only after the other owners have returned their new files; use a backup first.

## Your deliverables

- Updated `static/index.html`.
- A minimal change to `app.py` only if new endpoints are needed for the new modules.
- Optional `test_priority2_api.py` to validate new endpoints.

Do not edit `attribution.py`, existing checkers, golden fixtures or presets unless you explicitly document why a shared fixture change is unavoidable and approve it as integrator. Keep all existing Priority 1 behavior working.

## Frontend requirements

1. **Interactive statement replay:** use actual `attribution.epochs`. Add Previous/Next controls or a stepper. For the selected event display timestamp, transaction ID, credit/debit, event amount, `ledger_balance`, `clean_balance`, `tainted_pool` and the event note. Use API data; don't calculate any rupee values in JS.
2. **Three scenario cards:**
   - “Broad account restriction — illustrative balance affected” using actual balance data and clearly labelled assumptions.
   - “Amount-limited scenario — illustrative comparison” using the backend impact and attribution metrics already computed.
   - “Further review required” using actual unresolved review flags/ambiguity; do not invent an amount or pretend this is an official legal recommendation.
   Distinguish cash held from digital service access. Never call un-attributed balance “innocent” or “legally cleared.”
3. **Review flags:** after A/B/C hand off their modules, use `review_flags.build_review_flags`, `invariants.check_case_invariants` / stress test, and `victim_explainer.explain_victims` via a small, clear API surface. Suggested endpoints: `GET /api/analysis-extras/{preset_id}` and `GET /api/stress-test?n=40&seed=7`. Keep existing `/api/analyze-case` response contract stable.
4. **Actual stress-test panel:** display case count, seed, passed/failed checks and failure details from `stress_test.run_stress_test`. Never hardcode “40/40 passed.”
5. **Victim explanations:** show the deterministic template output from the backend.
6. **Evidence demonstration:** show what the existing merchant fixture actually returns. Do not fake an unmatched invoice result. If the mismatch fixture is not exposed as a real input/preset, keep it as an automated test and label it accordingly rather than inventing a UI case.

## UI/security constraints

- Single self-contained `static/index.html`; vanilla HTML/CSS/JS only, no React, npm, external URLs, CDNs or internet fonts.
- Use safe DOM creation and `textContent` for API data, no unsafe injection of untrusted content.
- No rupee arithmetic in browser JS; format server-returned money strings only.
- Show loading states, empty states and endpoint errors. If new endpoint fails, the main Priority 1 dashboard must still work.
- Clear legend for verified information, model assumptions, unresolved questions and synthetic data.
- Professional, accessible, judge-readable design; avoid clutter and decorative charts that obscure calculations.

## Handoff/integration rules

Merge A/B/C's *new standalone files only* after they pass their own tests. Add optional API endpoints in `app.py` only after inspecting the real function signatures. Don't change the old output contract unless a documented, approved integration requirement demands it. Run all Priority 1 checks again plus the new tests, then manually click through the replay and scenario cards.

Return complete changed files and an integration report listing exact checks run and actual outputs. Do not claim Priority 2 is done if a check fails.
