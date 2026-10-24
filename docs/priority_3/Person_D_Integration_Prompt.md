# COPY/PASTE FOLLOW-UP PROMPT — PERSON D, PRIORITY 3 ACCEPTANCE

Inspect the actual new files supplied by A/B/C (`chain.py`, `sensitivity.py`, `audit_integrity.py` and their tests). Do not assume they exist or passed. Run each provided `unittest` suite and inspect its output before wiring any UI.

Only connect a feature whose implementation and tests are passing. Keep the previous dashboard intact. Add minimal optional `app.py` routes for the chain graph, sensitivity output and audit fingerprint if needed. Keep rupee calculations server-side and all generated numeric results bound to actual API output.

Run the Priority 1 checker and every Priority 2/3 unit test. Test the live UI. Verify a changed report payload causes fingerprint verification to fail, and that a graph with a missing counterparty appears unresolved rather than falsely connected. If sensitivity does not match the baseline cases, do not show its scenario amounts in the main demo; revert/hide it and list it as future work.

Send the final modified `static/index.html`, any justified `app.py` changes and a concise verification report. Do not claim a stretch feature is implemented just because a placeholder panel exists.
