# Mercy Ledger — Additional Features & Judge-Facing Implementation Plan

**Purpose:** Extend the current hackathon prototype without replacing the existing `attribution.py` engine or destabilizing the team's shared data contract.

**Implementation companion:** `mercy_ledger_enhancements.py`  
**Tests for the companion module:** `test_mercy_ledger_enhancements.py`

> **Build principle:** finish and test the existing MVP first. Enhancements are optional layers. Do not edit golden files to force a PASS, do not invent demo metrics, and do not describe a visualized candidate transfer path as proof of ownership or criminal intent.

> **Archive status note:** in the `mercy_ledger_attribution_ready.zip` available during preparation of this pack, `attribution.py` contains the implemented engine, but `simulator.py`, `triage.py`, `sla.py`, `impact.py`, `grievance.py`, and `orders.py` still contain stub markers, and `static/index.html` is still a placeholder. If teammates have newer files in their own working copies, inspect those copies before integrating; do not overwrite newer work with the older ZIP. This enhancement pack does not finish those base modules.

---

## 1. What additional changes make Mercy Ledger stronger?

The goal is to move the demonstration beyond a set of forms and summary cards. Each important amount should be explainable, reconciled, and tied to the records and assumptions used to produce it.

### A. Fund-conservation and invariant checks — backend correctness

Add measured checks that verify:

- Opening balance + credits − debits = calculated closing balance.
- Each replayed ledger balance agrees with the original statement sequence.
- At each replay step, clean balance + still-attributed pool = ledger balance.
- For each victim in the current model, disputed amount reconciles to remaining attributed amount + amount allocated to outgoing debits, within the documented rounding tolerance.
- Clean/ring-fenced balance + remaining attributed amounts = closing balance.
- The sum of per-victim provisional holds agrees with the reported provisional-hold total.

**Implementation:** use `check_conservation(case, attribution_result)` in the companion module. It returns a measured report, not a hardcoded success count. It does not modify attribution results or legal recommendations.

**Judge-facing benefit:** show a “Financial consistency” panel with the actual checks passed/failed, and allow a failed check to expand into the exact discrepancy. Label this as software consistency testing, not real-world fraud-detection accuracy.

### B. Stress-test runner — evidence of reliability

Run actual cases through `attribution.analyze_attribution` and then through the conservation checks. Once Person A has completed and validated `simulator.py`, feed it a deterministic set of generated synthetic cases using a fixed seed.

**Implementation:** `run_stress_test(cases, analyze_fn=attribution.analyze_attribution)` in the companion module.

**Rules:**

- The panel must display actual counts and the seed used.
- Show number of cases requested, executed, passed and failed.
- Allow users to expand failing cases and inspect the invariant that failed.
- Do not show “40/40 passed” unless 40 cases were actually generated, analyzed and checked during that run.
- Synthetic software tests do not establish accuracy on real fraud investigations.

**Judge-facing benefit:** concrete, reproducible proof that the engine checks itself.

### C. Multi-account transfer-link graph — controlled prototype

Add a graph that connects account statements using matching transfer records. Each account is a node; a matched debit/credit pair is an edge. Each edge should show amount, UTR, transaction references and timestamps.

**Implementation:** the companion module provides:

- `match_cross_account_transfers(transactions)` — matches unique debit/credit pairs using UTR and amount, checks timestamps and optional counterparty identifiers, and returns matched, ambiguous, unmatched and invalid rows.
- `trace_candidate_paths(transactions, start_account_id, after_timestamp, max_hops=5)` — enumerates candidate transaction paths from the supplied multi-account dataset.

**Required input fields:** each row must include `account_id`, `txn_id`, `timestamp`, `type`, `amount`, and `utr`. An optional `counterparty_account_id` strengthens matching. The existing single-account contract does not contain all of these fields, so the graph demonstration needs a separate synthetic multi-account fixture or a deliberately designed extension approved by the integrator.

**Critical limitation:** this version traces record-level transaction links; it does **not** prove that the same individual rupees remained identifiable after funds were commingled. It does not propagate a victim-level attributed amount through every hop. A complete multi-hop attribution algorithm would require a broader schema and careful treatment of mixed victim pools, splits, partial debits and cycles. Do not claim that this companion module solves that larger problem.

**Match labels:**

- `COUNTERPARTY_FIELDS_CORROBORATE` — UTR and amount match, timestamps are consistent, and both supplied counterparty fields agree.
- `UTR_AMOUNT_CANDIDATE` — unique UTR and amount match, but mutual counterparty fields were not supplied.
- `Ambiguous` / `Unmatched` — conflicting, duplicated, missing or insufficient records.

Even the strongest status means the supplied records corroborate a transaction link; it does not prove the account holder's intent, guilt, or the provenance of money after commingling.

**Judge-facing benefit:** a clickable chain diagram with honest link status and an “evidence behind this link” panel. Use synthetic accounts and a visible “Synthetic demo data” label.

### D. Assumption sensitivity panel — expose model dependency

The current `attribution.py` documents a project assumption that debits consume attributed/disputed funds before clean funds. The data contract explicitly says that the SOP does not state a universal debit-ordering algorithm. This should remain visible.

**Implementation:** `run_assumption_sensitivity(case)` compares three simplified single-account hypotheses:

1. `DISPUTED_FIRST` — debits consume the attributed pool before clean funds.
2. `PROPORTIONAL` — each debit reduces clean and attributed balances in proportion to the current ledger composition.
3. `CLEAN_FIRST` — debits consume clean funds before the attributed pool.

**Display:** put the current configured model first and the alternative hypotheses beside it. For each, show remaining attributed amount by victim, amount allocated to outgoing debits and remaining clean balance. Let a judge click a transaction to compare the scenario replay.

**Important:** these modes are analytical alternatives, not three SOP-approved methods. Do not call their range “the legally restorable amount.” Keep the SOP-derived primary result and its golden tests unchanged. Use a synthetic sensitivity-specific example if the selected SOP illustration does not demonstrate materially different outputs.

**Judge-facing benefit:** your project shows not only its result, but also how sensitive that result is to an explicitly stated assumption.

### E. Tamper-evident report fingerprint — integrity aid

Attach a SHA-256 digest calculated from a canonical JSON representation of the input case, engine version and output. Include a “Re-verify report” action that recomputes the digest.

**Implementation:**

- `create_audit_manifest(inputs, output, engine_version)`
- `verify_audit_manifest(inputs, output, manifest)`

**Important:** the digest can show whether the current payload matches a recorded digest. It does not by itself prove who created a report, that source records are authentic, that the arithmetic is legally correct, or that the report is admissible. To detect edits by someone who can change both report and digest, preserve the digest in a separately controlled location or use an appropriate digital-signature mechanism in a future version.

**Judge-facing benefit:** an integrity badge with “Matches saved fingerprint” or “Digest mismatch,” accompanied by the SHA-256 fingerprint and a short explanation of its limitation.

### F. Plain-language explanation per victim — human-readable reasoning

Generate a neutral fixed-template explanation from the backend's existing victim output. It should show:

- Reported disputed amount.
- Amount remaining attributed in the analyzed account under the configured model.
- Amount allocated to outgoing debit(s).
- Attribution method.
- Difference between provisional complaint-order hold and attribution-derived remaining amount, where applicable.
- Outgoing transaction references and times; explicitly state when the receiving account is not available in the supplied data.

**Implementation:** `build_victim_explainer(case, attribution_result, complaint_id)`.

**Judge-facing benefit:** a “Explain this result” drawer that translates a calculation into plain language, while retaining a link to the underlying transaction rows. Do not write “your money has been recovered” unless the system has a source field that actually confirms restoration.

---

## 2. Visual changes to make the demo stronger for judges

The interface should feel like a financial-investigation workbench: calm, professional, readable on a projector, and explainable at a glance. Avoid adding decorative charts that do not improve understanding.

### Recommended case-analysis screen

1. **Top-level status strip**
   - Selected case ID and label, plus a visible `Synthetic demo data` label for invented cases.
   - Server status (`Live server` or `Offline demo data`, if the current frontend supports it).
   - Number of analysis errors/warnings.

2. **Four KPI cards**
   - Total disputed amount reported in the case.
   - Amount currently attributed/remaining under the model.
   - Amount allocated to outgoing debits.
   - Clean balance / balance not currently attributed by the model.

   All values must come from backend responses. Every card should have a small “How calculated” explanation. Do not label un-attributed money “confirmed innocent.”

3. **Central fund movement panel**
   - Use a directed graph only when multi-account data is present.
   - Use distinct line styles and text labels for corroborated, candidate and ambiguous links; do not rely on color alone.
   - Selecting a link opens transaction IDs, UTR, amount, timestamps and the matching basis.
   - If no multi-account data is available, show the chronological single-account replay instead of a misleading graph.

4. **Interactive statement replay stepper**
   - `Previous transaction` / `Next transaction` controls.
   - Current event displayed prominently: timestamp, debit/credit, amount and UTR.
   - Running ledger balance, clean balance and per-victim attributed pool after that event.
   - Short explanation using the engine's `note` field.
   - A progress indicator such as “Transaction 4 of 12.”
   - Do not recompute money amounts in JavaScript; the stepper displays supplied backend epoch values.

5. **Restriction-impact scenario cards**
   - **Scenario A — Broad account restriction:** show the full balance potentially affected under the selected hypothetical.
   - **Scenario B — Amount-limited scenario:** show the configured disputed/attributed amount and the additional balance not currently attributed by the model.
   - **Scenario C — Further review required:** show why ambiguous links, competing claims or incomplete evidence prevent a reliable amount from being determined.

   Every card must be labelled “Hypothetical decision support — not an order.” Distinguish a cash lien from digital-channel suspension; do not imply that the latter necessarily locks the account's entire cash balance. Show the same case data across scenarios so the comparison is fair.

6. **Victim allocation table**
   - One row per victim with disputed amount, provisional hold, remaining attributed amount, amount allocated to outgoing debits and method.
   - Add an explicit flag when the complaint-order hold differs from the attribution-derived amount. Call it “Review discrepancy,” not “unlawful hold.”
   - Clicking a row opens the plain-language victim explanation and source transactions.

7. **Evidence and uncertainty panel**
   - Clearly separate transaction-link status from evidence about a person's intent.
   - Show `Matched`, `Mismatch`, `Missing evidence`, `Candidate link`, or `Unresolved` with both text and visual treatment.
   - Merchant invoices and delivery records are supporting evidence, not automatic proof of innocence.

8. **Financial-consistency / stress-test panel**
   - Display actual measured check totals from `run_stress_test`.
   - Expand an individual check to show expected value, actual value and discrepancy.
   - Label the dataset as `SOP-derived scenario` or `Synthetic software test` as appropriate.

9. **Assumption comparison drawer**
   - Present disputed-first / proportional / clean-first only as named hypotheses.
   - Keep the primary configured result visually distinct from alternatives.
   - Include the disclaimer that alternatives are not all SOP-mandated methods.

10. **Report area**
    - “Explain this case” summary.
    - Export/download only if the existing application supports it safely.
    - Show the SHA-256 manifest status if the audit helper has been connected.
    - Display limitations and warnings alongside the result, not hidden only in a footer.

### Suggested design system

- **Base:** off-white or very light grey background; deep navy header; white cards.
- **Accent:** one restrained teal/blue for primary actions and focus states.
- **Status colors:** green = corroborated/passed; amber = requires review; red = failed check or conflict; grey = missing/not available. Always pair color with readable text/icons.
- **Typography:** body text at least 15–16 px; primary amounts 28–34 px; table text 14–15 px minimum.
- **Spacing:** generous card padding and clear group headings. Avoid dense walls of tiny numbers.
- **Charts:** use a graph for transfer relationships, a bar for restriction-impact comparison and a stepper for time sequence. Each visualization should answer one question.
- **Responsive layout:** works at 1280 px for projection and 390 px on mobile, with overflow contained inside tables.
- **Offline resilience:** if the current frontend supports sample fallback, show a visible offline badge. Never imply cached examples are live analysis.

---

## 3. How to integrate the companion implementation

### New standalone files

- `mercy_ledger_enhancements.py` — utility functions listed below.
- `test_mercy_ledger_enhancements.py` — tests for the utilities using the checked-in synthetic/demo presets and small synthetic multi-account rows.

The companion module does **not** modify `attribution.py`, the goldens, `pipeline.py`, or `app.py`.

### Integration snippets

Run inside the extracted `mercy_ledger` directory after copying the two files there:

```python
import attribution
import presets
import mercy_ledger_enhancements as enhancements

case = presets.get_preset("SOP_ILL_1")
analysis = attribution.analyze_attribution(case)

# A. Check the current result's financial invariants.
invariant_report = enhancements.check_conservation(case, analysis)

# B. Measure the test cases you actually ran.
stress_report = enhancements.run_stress_test(
    list(presets.PRESETS.values()),
    analyze_fn=attribution.analyze_attribution,
)

# C. Compare debit-consumption assumptions in a clearly labelled sensitivity view.
sensitivity = enhancements.run_assumption_sensitivity(case)

# D. Explain one victim's result.
victim_explanation = enhancements.build_victim_explainer(
    case, analysis, analysis["victims"][0]["complaint_id"]
)

# E. Fingerprint a case result and verify it later.
manifest = enhancements.create_audit_manifest(case, analysis, "attribution-current")
verification = enhancements.verify_audit_manifest(case, analysis, manifest)
```

Cross-account link matching and candidate path generation require a separate dataset containing `account_id` and optional `counterparty_account_id` fields; those fields are not present in the current single-account transaction contract.

### Optional API routes (integrator only)

After core tests pass, the integrator may add small FastAPI routes in `app.py` that wrap the functions; teammates should not edit `app.py` independently. Suggested endpoints:

- `POST /api/enhancements/transfer-links` — returns matching, ambiguous, unmatched and invalid transfer rows.
- `POST /api/enhancements/trace-paths` — returns candidate paths from a synthetic multi-account dataset.
- `POST /api/enhancements/sensitivity` — returns the three single-account assumption scenarios.
- `POST /api/enhancements/stress-test` — accepts only an approved count/seed, uses the validated simulator and returns actual invariant-check totals.
- `POST /api/enhancements/audit-manifest` — returns a fingerprint for the supplied case result.

Validate request bodies, limit the number of rows/cases, handle errors visibly, and do not add live banking calls.

---

## 4. Recommended execution order under a tight deadline

1. **Core first:** run the attribution checker and finish the original teammate-assigned modules. Do not add these features to compensate for a failing base project.
2. **Add invariant checks:** copy the companion module and test file into the project. Run `python -m unittest test_mercy_ledger_enhancements.py` from the project folder.
3. **Build the replay and scenario cards:** use existing backend epoch and impact fields. This is the highest visual return for the lowest risk.
4. **Add the measured stress-test panel:** only after `simulator.py` creates genuinely distinct seeded cases and passes its checker.
5. **Add the small graph fixture:** only if multi-account matching data and time are available. Label paths as candidates, not per-rupee proof.
6. **Add sensitivity and victim explainer:** keep sensitivity clearly hypothetical; explain results from backend fields.
7. **Add audit fingerprint:** only after report contents are stable.
8. **Freeze, run the full checker, restart cleanly, and rehearse.** No new feature is worth breaking the demo.

### Suggested ownership

- **Person A:** finish `simulator.py` first, then help with conservation/stress tests if time remains. Don't modify `attribution.py`.
- **Person B:** finish `triage.py`, `sla.py`, `impact.py` and provide the fields the scenario cards need.
- **Person C:** finish `grievance.py`, `orders.py` and ensure generated text is escaped and labelled as a draft.
- **Person D / integrator:** own `static/index.html`, API wiring, optional endpoints, full test run and demo rehearsal.

### Stop conditions

- If the core checker fails, stop adding enhancements and fix the core.
- If chain links are ambiguous, show them as unresolved rather than choosing one automatically.
- If the stress test repeats canned presets, don't call it a randomized stress test.
- If the sensitivity output isn't materially different for the chosen example, use a separately labelled synthetic sensitivity fixture; do not claim a difference the data doesn't show.
- If the hash isn't checked against a separately preserved digest, call it a report fingerprint, not secure proof of authorship.

---

## 5. What to say to judges

**Technical contribution:**

> “Our contribution is an explainable reconciliation workflow. It combines deterministic attribution with financial invariant checks, exposes differences between provisional complaint-order holds and attribution results, and lets reviewers inspect the transaction-level reasoning. In the extension, we can also match cross-account transfer records and show candidate paths, but we clearly label what the available data can and cannot prove.”

**Why not just use ML?**

> “The rupee calculations need to be deterministic and auditable. A classifier doesn't resolve the accounting problem. We use explicit rules and tests for the financial arithmetic, and we do not interpret a transaction pattern as proof of guilt.”

**What is the limitation of the graph?**

> “A matching UTR and amount can link transaction records, but the graph alone can't tell us which exact rupees remain attributable after commingling. A fully verified multi-hop attribution engine would need richer multi-account data and a separately validated propagation algorithm.”

**Does the hash prove the report is legally valid?**

> “No. SHA-256 detects whether the payload matches a recorded digest. It doesn't prove source authenticity, authorship or legal correctness.”

**What can the prototype guarantee?**

> “Only the outcomes of the specific implemented rules and tests. It doesn't guarantee victim recovery, declare an account holder guilty or innocent, or authorize restrictions.”

---

## 6. Acceptance checklist

- [ ] Existing attribution and teammate module checkers pass before integration of optional enhancements.
- [ ] `python -m unittest test_mercy_ledger_enhancements.py` passes from the project folder.
- [ ] Stress-test values come from the cases actually run, not constants.
- [ ] Multi-account input has account IDs and a synthetic-data label.
- [ ] Missing/duplicated UTRs and amount conflicts show as ambiguous/unmatched.
- [ ] Every graph link exposes its UTR, amount, timestamps, source and destination transaction IDs.
- [ ] No visualization implies that a candidate transaction link proves criminal intent or per-rupee lineage.
- [ ] Replay displays backend-generated epochs; browser JavaScript does not calculate rupee attribution.
- [ ] Restriction scenarios are marked hypothetical and distinguish cash restrictions from digital-channel suspension.
- [ ] Sensitivity results are labeled as alternative assumptions, not legal entitlements or SOP-mandated options.
- [ ] Audit fingerprint re-verification detects a changed input/output and explains the hash's limitations.
- [ ] Synthetic cases and SOP-derived cases are labelled separately.
- [ ] The final app starts cleanly and the end-to-end demo has been rehearsed.
