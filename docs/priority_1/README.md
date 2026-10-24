# Priority 1 — Core MVP (mandatory gate)

**Goal:** one usable end-to-end app using the existing contract. No new graph, sensitivity, hashing or other stretch feature during this phase.

## Parallel owners

- **Person A:** `simulator.py` only. Preserve `attribution.py`.
- **Person B:** `triage.py`, `sla.py`, `impact.py`.
- **Person C:** `grievance.py`, `orders.py`.
- **Person D:** `static/index.html`; then integrate all returned modules and run the full checker.

Paste the role-specific prompt into the coding AI after opening the baseline project directory. A, B and C return only their named complete files to D.

## Must work before moving on

- Existing attribution checker passes.
- Each assigned module checker passes.
- `python check_my_work.py all` reports success after integration.
- Frontend displays live API results, actual errors, readable statement epochs, victims, review indicators, grievance checks and draft documents supported by the backend.
- Offline fallback is clearly labelled as demo data and is generated only after the full checker passes.
- App starts from a clean terminal and can be demonstrated end to end.

See `ACCEPTANCE_GATE.md`. Do not start Priority 2 until that gate passes.
