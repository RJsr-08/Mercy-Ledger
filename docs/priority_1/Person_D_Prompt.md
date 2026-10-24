# COPY/PASTE PROMPT — PERSON D, PRIORITY 1 FRONTEND

You are **Person D — Frontend Developer and Integrator**. I am the team lead. Inspect the actual Mercy Ledger project and build the UI while Persons A/B/C work in separate copies.

## Required reading

Read `README_START_HERE.md`, `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md`, `PERSON_4_FRONTEND.md`, `app.py`, `pipeline.py`, `presets.py`, `static/sample_data.js`, selected golden files and `check_my_work.py`.

## First deliverable while others work

Implement **`static/index.html` only** as one self-contained HTML/CSS/vanilla-JavaScript file. Keep the existing API contract and project stack. Do not add React, Tailwind, npm, CDNs, network fonts, network assets or new dependencies.

Build a calm, high-contrast financial-investigation dashboard with:
- Mercy Ledger title and visible Live Server / Offline Demo Data badge.
- Aggregate blanket-vs-proportionate impact panel from `/api/portfolio-impact`.
- Preset picker that calls `/api/presets` and `/api/analyze-case`.
- Case header, recommendation ladder, attribution/victim table, statement epochs, deadline clocks, merchant evidence checks and draft document tabs where the API provides data.
- Clear visible warnings when `errors` is non-empty or a section is unavailable.
- `textContent`/safe DOM construction for API text; do not inject untrusted data with `innerHTML`.
- Rupee formatting that preserves the server-provided money strings; JavaScript may format but must not calculate money.
- Responsive layout for projector/laptop and phone sizes; readable labels, good spacing, keyboard-accessible controls and clear status text.
- Offline sample fallback, visibly labelled and clearly not live analysis.

Do not hardcode calculated values as if they came from the backend. Do not implement the Priority 2/3 features in this phase. Keep the page functional even when a section is null or the server fails.

## After Persons A/B/C hand off files

Use the separate `Priority_1_Core_MVP/Person_D_Integration_Prompt.md`. Merge only their assigned files into the master copy, then run all checks and fix genuine integration issues.

## Output now

Save the complete `static/index.html` in the project copy and return that full file plus a concise report of manual checks actually performed. Do not modify `attribution.py`, golden files, checker or the shared data contract. If a shared-file change seems necessary, explain why before making it.
