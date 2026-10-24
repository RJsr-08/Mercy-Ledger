# Priority 3 Acceptance Gate

Only merge a stretch feature if its automated tests pass, its output is honestly labelled, and Priority 1 + Priority 2 still pass.

## Chain visualization
- [ ] Inputs contain explicit synthetic multi-account transactions and identifiers.
- [ ] Matching labels differentiate verified links from candidate/inferred links.
- [ ] Missing destination details become unresolved links, never invented edges.
- [ ] Splits and repeated hops do not inflate the original principal. Do not sum the same amount across every edge as though it were newly recoverable at each hop.
- [ ] Commingling limitations are visible, and no exact per-rupee downstream lineage is claimed unless the input and algorithm support it.

## Sensitivity analysis
- [ ] Each scenario's debit-consumption rule is documented and labelled as an analytical assumption.
- [ ] Output uses terms like `scenario_remaining_attributed` rather than presenting hypothetical amounts as legal restoration decisions.
- [ ] The baseline scenario agrees with the current attribution engine on the selected cases, or the feature reports a mismatch and is not presented as validated.
- [ ] No change was made to `attribution.py`.

## Audit fingerprint
- [ ] Canonical JSON serialization is deterministic (`sort_keys`, stable separators, fixed encoding).
- [ ] One-byte change to input or output causes verification to fail.
- [ ] Same payload with same engine version produces the same digest.
- [ ] UI clearly says this is a fingerprint, not proof of authenticity, legal correctness or authorship.

## Final checks

```bash
python -m unittest test_priority3_chain.py
python -m unittest test_priority3_sensitivity.py
python -m unittest test_priority3_audit_integrity.py
python check_my_work.py all
```

Only run commands for files that were actually implemented. Then start the app and run the main demo from a clean terminal. If any stretch item fails, remove that item from the UI and pitch it as future work instead of showing an unverified result.
