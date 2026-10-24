# COPY/PASTE FOLLOW-UP PROMPT — PERSON D, PRIORITY 2 INTEGRATION

The Priority 1 baseline is passing. I have received the following new files from teammates: `invariants.py`, `stress_test.py`, `test_priority2_invariants.py`, `review_flags.py`, `test_priority2_review_flags.py`, `victim_explainer.py`, and `test_priority2_explainer.py`. Inspect which files are actually present; do not assume missing files exist.

1. Read their module docstrings and inspect function signatures before wiring them.
2. Add only the minimal new API endpoints in `app.py` needed by the existing UI. Prefer keeping `/api/analyze-case` and the original pipeline return schema unchanged.
3. Ensure endpoint failures return a visible error and do not crash the core dashboard.
4. Integrate the already implemented UI replay/scenario cards using true backend results.
5. Run every new `unittest` file and `python check_my_work.py all`.
6. Start the app and verify each preset. Test no-data/error states and offline fallback.
7. If any existing Priority 1 check fails after the merge, resolve or revert the Priority 2 change before accepting it.
8. Do not modify the checkers or golden files to manufacture a pass, and do not start Priority 3 until the full gate passes.

Provide the full modified `static/index.html` and any integrator-owned `app.py` changes, plus exact test output and any remaining issues.
