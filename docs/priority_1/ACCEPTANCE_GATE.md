# Priority 1 Acceptance Gate

## Automated checks

From the project root:

```bash
python check_my_work.py attribution
python check_my_work.py simulator
python check_my_work.py triage
python check_my_work.py sla
python check_my_work.py impact
python check_my_work.py grievance
python check_my_work.py orders
python check_my_work.py all
```

All must pass after integration. Do not edit `check_my_work.py` or golden files to make a check pass.

After all checks pass:

```bash
python make_sample_data.py
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` locally. Stop the server and verify the UI clearly falls back to labelled offline demo data if supported by the implementation.

## Manual demo checklist

- [ ] Load each existing preset; all displayed sections refresh consistently.
- [ ] Test selected Annexure-V cases against documented expected results.
- [ ] Confirm amounts use Indian grouping and no monetary math is performed in browser JavaScript.
- [ ] Confirm draft documents are labelled for review and are rendered safely.
- [ ] Confirm non-empty API `errors` and unavailable sections are visible.
- [ ] Confirm an account holder is not called guilty/innocent by a scorecard or invoice match.
- [ ] Confirm `SUSPENSION_REVIEW_45D` is labelled `PROPOSED POLICY - NOT an SOP clause` if shown.
- [ ] Confirm the app can start from a clean terminal and a 2–3 minute demo is possible.

**Gate decision:** If any automated checker or core workflow fails, stay in Priority 1. Do not add Priority 2 features yet.
