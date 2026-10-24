# Quick Role Map

| Priority | Person A | Person B | Person C | Person D (integrator) |
|---|---|---|---|---|
| **P1 Core MVP** | `simulator.py` | `triage.py`, `sla.py`, `impact.py` | `grievance.py`, `orders.py` | `static/index.html`; then merges A/B/C and runs full checker |
| **P2 Judge-value** | `invariants.py`, `stress_test.py`, tests | `review_flags.py`, tests | `victim_explainer.py`, tests | Replay stepper + scenario cards + optional endpoints and integration |
| **P3 Stretch** | `chain.py`, tests | `sensitivity.py`, tests | `audit_integrity.py`, tests | Graph/sensitivity/hash UI and minimal optional endpoints |

P2/P3 modules are new stand-alone files so they can be removed if time gets short. D remains sole owner of `app.py`, `pipeline.py`, `presets.py`, the shared data contract, checkers, golden fixtures and integration changes. Ask D before changing any of those shared assets.

## Merge order

After each priority, receive complete files, back up master, copy only assigned files, run all tests, manually demonstrate the application, then decide whether to unlock the next priority.
