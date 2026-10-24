# Priority 3 — Stretch Features (optional; only after Priority 2 passes)

Priority 3 is not required for a credible demo. Start it only if the team has remaining time and Priority 1+2 remain stable. Do not start every feature blindly; any failing stretch feature must be omitted rather than allowed to destabilize the working application.

## Parallel owners

- **A:** `chain.py`, `test_priority3_chain.py` — controlled synthetic multi-account transfer-link graph.
- **B:** `sensitivity.py`, `test_priority3_sensitivity.py` — explicitly hypothetical debit-allocation scenario analysis.
- **C:** `audit_integrity.py`, `test_priority3_audit_integrity.py` — canonical SHA-256 report fingerprint and re-verification.
- **D:** graph/sensitivity/integrity UI and minimal optional `app.py` endpoints, after receiving the modules.

## Guardrails

- Do not edit the current `attribution.py` API or re-write its implementation.
- Link visualization is not proof of exact per-rupee provenance after commingling. It may show verified links (matching provided cross-account identifiers), candidate links, and unresolved transfers.
- Sensitivity scenarios are assumptions used for robustness analysis, not legal attribution rules or amounts declared legally recoverable. The existing configured baseline remains primary; if an alternative model cannot be validated against its stated assumptions, omit it.
- SHA-256 fingerprint verification proves only that the canonical payload matches the compared digest. If both the report and its digest can be edited, this is not a signature or proof of authorship/authenticity.
- No live bank or overseas tracing, company registry lookup or CFCFRMS integration is included.

See `ACCEPTANCE_GATE.md`. A stretch feature that is not verified should be left out of the final demo.
