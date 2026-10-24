# PERSON 2 - THE RULEBOOK ("Triage, Deadlines, Impact")

**You deliver 3 files:** `triage.py`, `sla.py`, `impact.py`.
You turn the numbers from Person 1 into a *recommendation* (how hard to restrict the account), *deadline clocks*, and the *before-vs-after* savings.

---
## STEP 0 - Set-up (10 minutes, once)
1. Install Python 3.11+ from python.org (Windows: tick "Add Python to PATH").
2. Unzip `mercy_ledger`, open a terminal INSIDE the folder.
3. Run `python check_my_work.py triage` (Mac: `python3`). It says FAIL ("still the STUB") - good, it works.

## STEP 1 - Copy-paste this to your AI (attach the whole folder; or paste `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md`, this file, and the `golden/` files: SOP_ILL_1, SOP_ILL_2, MERCHANT_200, EXTRA_MIXED, EXTRA_ESCROW with `.case.json`, `.attribution.json`, `.grievance.json`, `.triage.json`, `.sla.json`, `.impact.json`, plus `PRESETS.aggregate_impact.json` and the two `SOP_ILL_1.sla.asof_*.json`)
> You are helping build one part of a hackathon project. Read `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md` and `PERSON_2_TRIAGE_SLA_IMPACT.md` completely and obey them exactly. Write the COMPLETE files `triage.py`, `sla.py` and `impact.py`. Copy every text string (labels, citations, rationales, SOP references, notes, disclaimer) character-for-character from the golden files. Reply with only the three files, each in its own code block with the file name above it. If anything is unclear, ask me instead of guessing.

## STEP 2 - Check, fix, repeat
Run `python check_my_work.py triage`, then `sla`, then `impact`. Each must say PASS. If FAIL, paste the PROBLEMS list to your AI: "Fix exactly these, change nothing else." Then send me the three files.

---
## `triage.py` - `triage(case, attribution, grievance=None) -> dict`
This is a **project-defined demo scorecard, not an official SOP scorecard and not a trained model.** Its weights and thresholds are illustrative and not validated on real bank outcomes.

**Inputs you use:** `case["complaints"]`, `case["account"]["account_type"]`, `attribution["balance_at_seizure"]`, the clean balance at the same reference timestamp (derive from the last `attribution["epochs"]` row at or before `case["seizure_timestamp"]`, or use the closing snapshot if no seizure timestamp), `attribution["metrics"]["min_pass_through_minutes"]`, and `grievance["all_disputed_matched"]` (treat `grievance=None` as "no documents matched").

**Metrics (Decimal):**
* `n` = number of complaints.
* `clean_share` = clean balance at the reference timestamp divided by `balance_at_seizure` (0 if balance is 0). Output rounded to 4 decimals as a string, e.g. `"0.0055"`.
* `fast` = `min_pass_through_minutes` is not null and `<= 30`.
* `special` = account_type is NODAL, POOL or ESCROW.
* `docs` = `grievance` exists and `all_disputed_matched` is true.

**Score = sum of these 6 factors, in this exact order** (list them all in `factors`, with `points` = 0 when not triggered, `triggered` true/false; copy `label` text from the golden file):
| key | triggers when | points |
|---|---|---|
| `victims3` | n >= 3 | +2 |
| `victims2` | n == 2 | +1 |
| `fast` | fast pass-through (<= 30 minutes) | +2 |
| `lowclean` | clean_share < 0.10 | +1 |
| `nodocs` | NOT docs | +1 |
| `docs` | docs | -2 |

**Decision (first rule that applies wins):**
1. `special` -> `TARGETED_LIEN_ONLY` (cite 9.1(iii))
2. `n <= 1` -> `TARGETED_LIEN_ONLY` (cite 9.1(i): escalation applies when reported multiple times)
3. score >= 5 -> `SEIZURE_S106`
4. score >= 3 -> `DIGITAL_SUSPENSION_PENDING_EDD`
5. otherwise -> `TARGETED_LIEN_ONLY`

`rationale`, `citations` (a list, order matters) and `disclaimer`: copy from the golden files; each decision path has its own golden example (Ill 1 = seizure, Ill 2 = suspension, MERCHANT_200 = targeted lien, EXTRA_ESCROW = special). `thresholds` = `{"seizure_at_or_above":5,"suspension_at_or_above":3,"fast_pass_through_minutes":30}`. `human_signoff_required` is always `true`.
`metrics` = `{complaints_count, clean_share_of_balance, min_pass_through_minutes, special_account, documents_match_all}`.

## `sla.py` - `compute_sla(case, as_of) -> list` (5 clocks, fixed order)
`as_of` is a date string. All counting is in **calendar days** (`datetime.date`). Never use today's date.
| key | starts on (from `case["sla_context"]`) | length | completed when | DUE_SOON when days_left <= |
|---|---|---|---|---|
| `BANK_GRIEVANCE_7D` | `account_holder_complaint_on` | 7 | `grievance_filed_on` is set | 2 |
| `IO_DECISION_15D` | `grievance_filed_on` | 15 | `io_decision_on` is set | 3 |
| `INTERIM_CUSTODY_15D` | `io_direction_on` (prototype meaning: bank received IO direction) | 15 | never (v1) | 3 |
| `HOLD_REVIEW_90D` | `grievance_filed_on` (bank submission date) | 90 calendar days (conditional review point, not automatic expiry) | never auto-complete in v1 | 15 |
| `SUSPENSION_REVIEW_45D` | `suspension_started_on` | 45 | never (v1) | 7 |

Per clock: if the start is null -> status `NOT_STARTED`, `deadline` null, `days_left` null. Else `deadline = start + length days`.
If completed -> `COMPLETED` (deadline filled, `days_left` null). Else `days_left = (deadline - as_of).days`; `< 0` -> `OVERDUE`; `<= due_soon` -> `DUE_SOON`; else `ON_TRACK`.
`label`, `sop_reference`, `note` strings: copy from golden. **Critical:** the 45-day clock's `sop_reference` is `"PROPOSED POLICY - NOT an SOP clause"`. Keep it exactly - the SOP has no 45-day cap and we must never claim it does.

## `impact.py`
`case_impact(case, attribution, triage) -> dict`:
* Use one reference timestamp for every money figure: `seizure_timestamp` if supplied; otherwise the closing snapshot.
* Derive clean balance at that timestamp from the last attribution epoch at or before it, or `opening_balance` if no event occurred yet. Do not use closing clean balance for a seizure-time metric when post-seizure transactions exist.
* `blanket_total_locked` = `attribution["balance_at_seizure"]` (or the selected closing snapshot when there is no seizure timestamp).
* `blanket_innocent_locked` = clean balance at the same reference timestamp.
* `mercy_innocent_locked` = clean balance at that reference timestamp only when recommendation is `SEIZURE_S106`; otherwise `"0.00"` for this **cash-restriction** metric. A digital-services suspension restricts channels, not necessarily cash balance, and its non-cash access impact is not quantified here.
* `innocent_capital_freed` = blanket_innocent_locked - mercy_innocent_locked.
* `victim_recoverable_preserved` = `victim_recoverable_in_blanket` = `attribution["totals"]["restorable_total"]` for this prototype.
* plus `case_id`, `title`, `recommendation`. This is a comparison metric, not proof that a real officer would impose either action.

`aggregate_impact(items) -> dict` over a list of IMPACT dicts: sums of the money fields; `reduction_percent` = `(blanket - mercy) * 100 / blanket` rounded to 2 dp string (`"0.00"` if blanket is 0); `victim_funds_preserved_percent` = `"100.00"` if the two victim sums are equal else the string `"<100"`; `by_recommendation` = counts; `per_case` = the items. Empty list must not crash (return zeros and `cases: 0`).
Use Decimal; ROUND_HALF_UP to 0.01.

---
## FORBIDDEN
`float(`, `datetime.now`, `date.today`, `import random`, AI/network libraries, extra keys, changed strings, modifying inputs.

## WHAT YOU MUST BE ABLE TO SAY TO THE JUDGES
1. **"Is the triage a machine-learning model?"** - "No, deliberately. A model trained on synthetic data proves nothing. It is a project-defined demo scorecard of six transparent rules, with cited SOP principles where applicable; its thresholds are not official or validated on real bank outcomes. Change a threshold and you see exactly why the answer changed."
2. **"Where do the thresholds (5, 3, 30 minutes, 10%) come from?"** - "They are policy parameters we chose for the demo, not validated on real data. They are constants at the top of the file; a bank's risk team would set their own. We say this in the output disclaimer."
3. **"Who decides?"** - "The Investigating Officer. Every recommendation says `human_signoff_required: true`. SOP Para 5(viii) lets the IO verify with the holder before any S.106(3) order."
4. **"Why three levels?"** - "SOP 9.1(i) lets banks hold only the disputed amount, suspend digital channels, or seize on LEA direction. SOP 5(ix) discourages unwarranted freezing. We recommend the least restrictive level the evidence supports."
5. **"What deadlines do you track?"** - "7 days for the bank to submit a grievance (Para 10.1(a)/10.2(b)); 15 days for the IO to decide (10.1(d)(e)); 15 days for the bank to complete interim custody (Process 1(v) (single victim) / Process 2(h) (multiple victims)); a conditional 90-day hold-review/removal workflow from bank grievance submission, with advance notice and exceptions under Para 10.1; it is not universal automatic expiry. The 45-day digital-suspension review is **our proposal**, clearly labelled - the SOP text has no 45-day rule."
6. **"How do you compute the impact and is it fair?"** - "We compare the estimated clean cash balance covered by a blanket monetary restraint with the cash covered by the selected demo recommendation. Digital-services suspension is not the same as cash being held; this metric does not quantify lost access to digital channels. Victim-recoverable amounts are held equal across the comparison by construction. The demo and synthetic cases illustrate assumptions, not a real-world forecast."
7. **"Deadline maths?"** - "Pure calendar-day arithmetic from the dates in the case file and an 'as of' date; no clock reads, so it's reproducible."
