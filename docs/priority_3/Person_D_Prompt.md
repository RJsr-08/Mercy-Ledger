# COPY/PASTE PROMPT — PERSON D, PRIORITY 3 INTEGRATION AND UI

You are **Person D — Stretch Feature Integrator**. Do not start until Priority 1 and 2 pass. Prioritize stability over feature count. Inspect the newly returned module signatures before any code changes.

## Your deliverables

- Updated `static/index.html`.
- Minimal additions to `app.py` for optional endpoints only if needed.
- Optional `test_priority3_api.py`.

Do not edit `attribution.py`, the core output contract, golden fixtures or existing checker.

## Integrate only if modules and tests are present and passing

- Add a “Multi-account links (synthetic demo)” view using `chain.trace_chains`. Show a visible “Synthetic sample” label and match-status legend. Verified links, candidate links and unresolved transfers must look different and have text labels, not just colors. A simple accessible SVG or CSS diagram is acceptable; no libraries/CDNs.
- Add “Assumption sensitivity” output from `sensitivity.analyze_sensitivity`; display the rules beside the scenario numbers. Explicitly state that this is a sensitivity experiment, not an official SOP rule or legal restoration amount. If validation against baseline fails, hide the feature and show it as not ready rather than displaying misleading numbers.
- Add a “Verify report fingerprint” action using `audit_integrity`. Display matching/mismatch result and the honest SHA-256 limitation. Do not say the hash proves authorship or legal admissibility.
- Keep the Priority 1 statement replay, attribution, scenario cards and Priority 2 checks working.

Potential endpoints can be added in `app.py`, such as `/api/chain-demo`, `/api/sensitivity/{preset_id}`, and a case-analysis fingerprint endpoint, but first inspect existing shapes and add only minimal routes. Never hardcode numerical outcomes into JavaScript.

## Acceptance

Run the Priority 3 module tests, the Priority 2 tests and `python check_my_work.py all`. Then test a clean startup. If any stretch feature breaks the baseline, revert that feature and leave the earlier priorities intact.

Return complete modified files, actual command output, a list of integrated features and a list of omitted/not-ready features. Be honest: if a graph edge lacks a verified recipient or if the sensitivity baseline does not match the core engine, the UI must say so.
