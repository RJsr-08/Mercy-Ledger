# Priority 2 — Judge-Visible Technical Depth (only after Priority 1 passes)

**Goal:** add verifiable analytical value without altering the finished attribution algorithm or breaking the shared contract. Everyone works in a separate copy again. Each addition must be removable without breaking Priority 1.

## Parallel tasks

- **A:** `invariants.py`, `stress_test.py`, and `test_priority2_invariants.py`.
- **B:** `review_flags.py` and `test_priority2_review_flags.py`.
- **C:** `victim_explainer.py` and `test_priority2_explainer.py`.
- **D:** UI improvements in `static/index.html`; integrate after handoff by adding minimal optional endpoints in `app.py` only if needed and test them.

## Priority 2 features

1. **Conservation invariants and real stress-test panel:** actual executed cases/checks, seed, pass/fail counts and inspectable failures—not hardcoded success badges.
2. **Review flags:** surface the gap between complaint-order hold totals and attribution-derived totals as a review prompt, never a finding of unlawfulness; show forwarded debits with unverified destinations as unresolved.
3. **Plain-language explanation:** fixed, deterministic template per victim with amount, method, retained-attributed amount, outflows and explicit limitations.
4. **Transaction replay:** a stepper driven by the existing `attribution.epochs` array, with previous/next controls and one event's balances/pool/note.
5. **Three scenario cards:** broad account-balance impact, amount-limited hypothetical impact, and “further review required.” Use backend figures and display assumptions. A scenario card is not a legal recommendation or authorization.
6. **Evidence demonstration:** display the current matching merchant scenario; test mismatches using existing fixtures where the runtime can genuinely load them. Do not fake a mismatched result or silently add unverified case data to presets.

## Critical rules

- Do not edit `attribution.py`, golden outputs or existing module checkers.
- Do not change existing return schema in a way that breaks Priority 1. New UI data may be served by optional endpoints added by D.
- `Decimal`, deterministic code, standard library only for new pure modules.
- The stress-test count must reflect tests actually run. Synthetic data is not evidence of accuracy on real cases.
- “SOP hold differs from attribution” is a **review flag** and not proof an existing hold is unlawful.
- Amount “not attributed by the model” is not automatically innocent or legally clear.

## Gate

See `ACCEPTANCE_GATE.md`. If Priority 1 fails after merging, rollback Priority 2 and restore the passing baseline. Don't start Priority 3 until Priority 2 passes.
