# Priority 2 Acceptance Gate

## New backend test expectations

- `invariants.py` reports individual checks and an actual `passed` boolean; it must not silently turn exceptions into passes.
- `stress_test.py` calls the existing seeded simulator and attribution engine, counts cases actually run, captures failures, and records the seed.
- Tests cover at least the two SOP-derived presets and one synthetic case, plus a deliberately invalid/mutated case that demonstrates the invariant detector fails visibly.
- `review_flags.py` produces explicit flag codes and explanations without calling an account holder guilty or declaring a hold unlawful.
- `victim_explainer.py` is deterministic and never claims funds were recovered unless verified restoration information is present in input.
- Every new module has automated tests that actually run and pass.

Example commands (use the exact test filenames delivered by A/B/C):

```bash
python -m unittest test_priority2_invariants.py
python -m unittest test_priority2_review_flags.py
python -m unittest test_priority2_explainer.py
python check_my_work.py all
```

## UI / integration gate

- [ ] Transaction replay uses the currently selected case's actual `attribution.epochs` output.
- [ ] Previous/next controls update event details and do not calculate balances in JavaScript.
- [ ] Three impact cards clearly label broad, amount-limited and further-review scenarios as hypothetical comparisons.
- [ ] Review flags and victim explanations come from backend endpoints, not hardcoded values.
- [ ] Stress-test panel displays actual run count, seed, passed checks and failures.
- [ ] Errors from optional endpoints are visible and do not blank the core dashboard.
- [ ] Merchant evidence says “matched/partial/not matched” or equivalent; it does not declare innocence/guilt.
- [ ] Priority 1 check suite still passes after new modules are merged.
- [ ] A 2–3 minute end-to-end demo remains possible.

Do not proceed to Priority 3 if any item fails. If the team has less than about an hour remaining, stop after the highest-value passing Priority 2 features; don't start the stretch work.
