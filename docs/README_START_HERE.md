# MERCY LEDGER — START HERE (team lead / integrator)

This package is a **starter kit in active development**, not a finished application. `attribution.py` is implemented and passes its golden-case checker. Six other backend modules and the frontend are still placeholders. Preset endpoints may return canned demo output while placeholders remain; that is not evidence that the full pipeline works.

## 1. What's included

- `PERSON_1_ATTRIBUTION_ENGINE.md`: deterministic synthetic test-case generator. The attribution engine itself is implemented in `attribution.py` and should not be overwritten.
- `PERSON_2_TRIAGE_SLA_IMPACT.md`: demo scorecard, deadline rules and impact metrics.
- `PERSON_3_GRIEVANCE_AND_ORDERS.md`: structured invoice checks and draft document generation.
- `PERSON_4_FRONTEND.md`: self-contained offline HTML/CSS/JavaScript interface.
- `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md`: shared instructions and frozen interfaces.
- `golden/`: expected output examples and additional test cases. Review all changes against the supplied SOP before changing these fixtures.
- `check_my_work.py`: module acceptance checker.
- `benchmark.py`: guarded benchmark that refuses to run while any required module is still a stub.
- `make_sample_data.py`: guarded offline-cache generator that refuses to regenerate from stubbed outputs.
- `app.py`, `pipeline.py`, `presets.py`: starter API and integration glue.
- `references/SOP_NCRP_CFCFRMS_2026-01-02.pdf`: supplied primary source SOP.

## 2. Team split — four people total

| Person | Owns | Responsibility |
|---|---|---|
| **You — Person 4 / team lead** | `static/index.html`, `app.py` integration, API contract coordination, end-to-end tests and pitch | Stitch/design refinement, frontend implementation, API wiring, merges and final demo |
| **Teammate A — Person 1** | `simulator.py` plus attribution regression review | Implement the seeded synthetic case generator; verify `attribution.py` with the checker but do not edit it without team-lead approval |
| **Teammate B — Person 2** | `triage.py`, `sla.py`, `impact.py` | Clearly labelled demo rules, correctly triggered deadlines and cash-impact metrics |
| **Teammate C — Person 3** | `grievance.py`, `orders.py` | Structured invoice consistency checks and HTML draft documents for officer review |

Only the owner edits their assigned module. The team lead owns shared contract changes and integrations. Do not have two AI agents change the same files in parallel.

## 3. Send this to each teammate

> Unzip the project. Read `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md`, and your assigned `PERSON_X_...md` completely. Use your preferred coding AI to implement only your assigned file(s). Run `python check_my_work.py <module>` until it says PASS, and send the finished files back to the team lead. Do not change golden files or shared contracts without approval. If the checker still fails after three focused attempts, send the exact error and PROBLEMS list to the team lead rather than rewriting other modules.

The attribution checker should now PASS. Other module checks are intentionally expected to FAIL while their files still contain `MERCY_LEDGER_STUB`.

## 4. Integration runbook

Run commands from inside the `mercy_ledger` folder.

1. Install Python 3.11 or later. Create a virtual environment if you know how; otherwise a fresh local environment is recommended.
2. Install the runtime dependencies once:

   ```bash
   python -m pip install -r requirements.txt
   ```

   On macOS, use `python3` in place of `python` if needed.

3. After each teammate finishes, copy only their deliverable files over the corresponding placeholder.
4. Run the full acceptance suite:

   ```bash
   python check_my_work.py all
   ```

   Expected success state: every module check and the whole-system pipeline check show PASS, followed by `ALL GOOD`. Do not ignore any failure.

5. Only after the full checker passes, refresh the offline fallback:

   ```bash
   python make_sample_data.py
   ```

6. Benchmark only after the full checker passes:

   ```bash
   python benchmark.py
   ```

   Do not make any speed claim unless the guard permits the benchmark to run and the actual implementation meets the stated threshold.

7. Start the server:

   ```bash
   python -m uvicorn app:app --host 127.0.0.1 --port 8000
   ```

   Open `http://127.0.0.1:8000` in your browser.

8. Test every preset twice, then disconnect Wi-Fi and restart the application. Verify the offline fallback was generated from the final implementation and that no stale cached result is shown.

## 5. Known scope limits (be honest in the pitch)

- `attribution.py` is implemented; `simulator.py`, `triage.py`, `sla.py`, `impact.py`, `grievance.py`, `orders.py` and `static/index.html` remain placeholders until their owners implement them.
- The initial schema records outgoing debit identifiers but lacks the receiving account identifier; it cannot prove a next-hop bank/account trace.
- CSV upload, live bank/CFCFRMS integration, OCR/PDF invoice extraction and production access controls are not part of the current starter implementation.
- The scorecard is project-defined demonstration logic, not an official MHA/I4C score or a model validated on real bank data.
- Draft documents are for officer review, not legally validated or court-ready orders.
- The 45-day checkpoint is a project-proposed review parameter, not an SOP clause.

## 6. Corrections grounded in the supplied SOP

1. **No general 45-day digital-suspension cap is stated in the supplied SOP.** The product must label this as `PROPOSED POLICY - NOT an SOP clause`.
2. **Attribution principle:** cite Para 5(xiii)(a)/(b) and Annexure-V. Para 5(xi) deals with a zero/insufficient balance and EDD; it is not the clean-balance attribution rule.
3. **15-day bank completion references:** use Para 11 Process 1(v) for the single-victim path and Process 2(h) for the multiple-victim path. Do not cite Process 1(h) for that requirement.
4. **90-day workflow:** this is a conditional grievance/hold review and potential removal process measured from bank grievance submission in the circumstances described by Para 10.1. It has conditions, advance notice, exceptions and possible extension. Do not describe it as universal automatic expiry.
5. **Tier 1 examples:** they are derived from Annexure-V, but the fixtures document a normalization of the printed Victim C complaint year in Illustration 1 and assumptions around times in Illustration 2. Do not claim fully verbatim reproduction.
6. **Merchant case:** `MERCHANT_200` is an invented illustration; do not attach unverified court-case names or citations.
7. **Debit allocation:** disputed-first is an explicit model assumption, not a universal debit rule stated in the SOP.
8. **System-gap claim:** do not claim CFCFRMS cannot perform a calculation or cannot access statements without evidence. Say Mercy Ledger automates and explains a reconciliation step using the supplied bank statement and complaint data.

## 7. Three-minute demo flow

1. Explain the restoration/reconciliation problem using the statistics printed in Section 2 of the supplied SOP (label them as figures reported by the SOP).
2. Open SOP-derived Illustration 1 and show provisional complaint-order holds beside the attribution output.
3. Open Illustration 2 and show pro-rata shares, then reconcile the shares to the available balance.
4. Open the illustrative merchant case and compare the potential cash restriction under the selected recommendation. Explain the metric's assumptions.
5. Show the deadline warnings and generated draft documents. Finish by stating that an authorized officer retains the final decision.

## 8. Final release checklist

- [ ] All seven backend modules are real implementations; no `MERCY_LEDGER_STUB` marker remains in required modules.
- [ ] `python check_my_work.py all` passes.
- [ ] Outputs match the two SOP-derived worked examples and all added tests.
- [ ] `python make_sample_data.py` succeeds after the final passing build.
- [ ] `python benchmark.py` only runs after guards pass; any public speed claim matches a recorded run.
- [ ] Full application works online and offline from a clean restart.
- [ ] No unverified court-case name, legal conclusion, universal deadline or real-world accuracy claim appears in the pitch.
