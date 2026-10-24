# PERSON 4 - THE WEBSITE ("Command Dashboard")

**You deliver 1 file:** `static/index.html` (a single self-contained file: HTML + CSS + JavaScript together).
You do not need the other people's code. The folder already runs a working demo server that returns realistic data for the 3 demo cases, so you can build and test right now.

---

## Frontend implementation constraint

For this starter package, the deliverable remains a self-contained `static/index.html` with inline CSS and vanilla JavaScript. Use Google Stitch for visual design inspiration if helpful, then implement within this constraint. Do not introduce React, Tailwind, npm or external CDNs unless the integrator first changes the shared setup and startup instructions for the whole team.

---
## STEP 0 - Set-up (10 minutes, once)
1. Install Python 3.11+ from python.org (Windows: tick "Add Python to PATH").
2. Unzip `mercy_ledger`. Open a terminal INSIDE the folder and run, once: `pip install fastapi uvicorn` (Mac: `pip3 install fastapi uvicorn`).
3. Start the server: `python -m uvicorn app:app --reload` (Mac: `python3 -m uvicorn app:app --reload`). Open http://127.0.0.1:8000 in your browser. You'll see a placeholder page. Leave the terminal running.
4. Whenever your AI gives you a new `index.html`, save it over `static/index.html` and refresh the browser.
   (Backup mode: you can also double-click `static/index.html` directly; it will show built-in sample data and a badge "Offline demo data".)

## STEP 1 - Copy-paste this to your AI (attach the whole folder; or paste `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md`, this file, and the contents of `golden/SOP_ILL_1.*.json`, `golden/SOP_ILL_2.attribution.json`, `golden/PRESETS.aggregate_impact.json`)
> You are helping build one part of a hackathon project. Read `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md` and `PERSON_4_FRONTEND.md` completely and obey them exactly. Write the COMPLETE single file `static/index.html` (HTML+CSS+vanilla JavaScript, no external libraries, no CDN, no fonts from the internet). Reply with only that file in one code block. If anything is unclear, ask me instead of guessing.

## STEP 2 - Test like a judge
Go through the "Acceptance checklist" at the bottom with your own eyes. Fix by telling the AI exactly what's wrong ("the SLA badges are not coloured"; attach a screenshot if it supports images). Then send me `index.html`.

---
## TECH RULES (non-negotiable)
* ONE file. Plain HTML/CSS/JS. **No frameworks, no npm, no build step, no external URLs of any kind** (venue Wi-Fi may fail; judges may be offline).
* The page must keep working if the server is unreachable: try the API first; on failure fall back to `window.SAMPLE` (loaded by `<script src="/static/sample_data.js"></script>` AND a second tag `<script src="sample_data.js"></script>`; one of the two will 404 harmlessly). Show a small badge "Live server" or "Offline demo data".
* API calls (relative URLs, no hard-coded host):
  * `GET /api/presets` -> list. Fallback `window.SAMPLE.PRESETS`
  * `POST /api/analyze-case` with JSON `{"preset_id":"SOP_ILL_1"}` -> full result (shape in `01_DATA_CONTRACT.md` section 3). Fallback `window.SAMPLE.CASES[id]`
  * `GET /api/portfolio-impact` -> `{aggregate, errors}`. Fallback `window.SAMPLE.PORTFOLIO`
* **Never calculate rupee amounts in JavaScript.** Every number comes from the API as a string. JavaScript may only (a) format a money string for display and (b) turn strings into numbers for drawing bar widths.
* Money display function `formatINR(str)`: handle by string slicing, no float. `"150000.00"` -> `₹1,50,000.00`; `"873.00"` -> `₹873.00`; `"485000.00"` -> `₹4,85,000.00`; `"1234567.50"` -> `₹12,34,567.50`; `"0.00"` -> `₹0.00`.
* **Security:** put API text into the page with `textContent` / `createElement`, never `innerHTML` with API data. Show the three order documents inside `<iframe sandbox="" srcdoc=...>` (sandbox attribute empty) - never inject their HTML into the page itself.
* Handle: loading state, `errors` array non-empty (show a visible yellow banner listing them), a section that is `null` (show "not available"), empty lists.
* Works on a laptop projector (1280px wide) AND a phone (390px wide, no sideways scrolling except inside wide tables).
* Readable from the back of a room: base font >= 15px, key numbers 28px+. Colour is never the only signal (use text/icons too).
* Look: calm, official, trustworthy (a government-tech feel, not a toy): off-white background, deep navy header, one accent colour, green/amber/red used only for status. Rounded cards, generous spacing.

## PAGE LAYOUT (top to bottom)
1. **Header**: "Mercy Ledger" + tagline "Freeze the fraud. Free the innocent." + the Live/Offline badge.
2. **Policy Impact Comparison Bar** (data: `aggregate` from portfolio-impact). Left card "Blanket freeze: innocent capital locked" = `blanket_innocent_locked`. Right card "Mercy Ledger: innocent capital locked" = `mercy_innocent_locked`. Centre: big "₹X freed" (`innocent_capital_freed`) and `reduction_percent` %. Small line: "Victims' recoverable money preserved: {victim_funds_preserved_percent}%". Caption: "Across {cases} cases (3 SOP/merchant cases + simulated stress-test cases)". Two proportional bars (width from the numbers) for blanket vs Mercy.
3. **Case picker**: one card per preset (title, tier chip: Tier 1 "SOP benchmark", Tier 2 "Illustrative merchant scenario", Tier 3 "Simulated"). Click -> loads the case. First preset auto-loads on page open.
4. **Case header**: title, description, account holder/type/layer, "as of {as_of}".
5. **Recommendation panel** (`triage`): a 3-step ladder `Targeted lien only` -> `Digital suspension pending EDD` -> `Section 106 BNSS seizure`, recommended step highlighted. Show `rationale`, the score and each `factor` (label, points, triggered or not), and `citations` as a list. A visible ribbon: "Decision support only - the Investigating Officer decides."
6. **Who gets what** (`attribution.victims`): a table, one row per victim: Victim | Disputed | SOP-style hold | Still in account (restorable) | Allocated to outgoing debits (not verified next-hop tracing) | Method badge (Direct / Pro-rata / Intact). Under it a summary strip: "SOP-style hold total {sop_complaint_order_hold_total}  vs  Right-sized hold {mercy_right_sized_hold_total}   |   Clean capital ring-fenced: {clean_ring_fenced}". For PRO_RATA rows show the `retention_ratio` as a percentage (use string manipulation or `Number()` for display only).
7. **Statement replay** (`attribution.epochs`): a timeline table: time, event (credit/debit + amount), who is still in the account (`tainted_pool` chips), clean balance, `note`. Time shown as readable text.
8. **Deadline clocks** (`sla`): five badge cards. Each: label, deadline date, days left, status colour (ON_TRACK green, DUE_SOON amber, OVERDUE red, COMPLETED grey-check, NOT_STARTED light grey), and `sop_reference`. The `SUSPENSION_REVIEW_45D` card must visibly carry the text from its `sop_reference` ("PROPOSED POLICY - NOT an SOP clause") as a tag.
9. **Merchant document check** (`grievance.results`): table: complaint, UTR, invoice, four checks as ✓/✗, verdict badge, reasons; then `disclaimer` in small text.
10. **Draft orders** (`orders`): three tabs (Restoration order, Indemnity bond schedule, EDD packet) showing the HTML in a sandboxed iframe. Below: a checkbox "I am the authorised officer and have reviewed these figures". Only when ticked are two buttons enabled: "Open in new tab" (Blob URL of the HTML) and "Download .html". Disabled buttons show why.
11. **How this was calculated** (collapsible): `attribution.assumptions` as a list, `warnings`, and a one-line note "No AI/ML is used for any amount or deadline."
12. **Footer**: "Mercy Ledger - decision-support prototype. Not legal advice. Demo data is illustrative; SOP Annexure-V figures are from the MHA/I4C SOP of 2 Jan 2026."

## ACCEPTANCE CHECKLIST (tick every box before sending)
- [ ] Page opens with the first case already loaded; no blank screen; no console errors.
- [ ] Click each of the 3 cases; every section refreshes.
- [ ] SOP_ILL_1 shows victims A ₹0.00 restorable / ₹97,000.00 forwarded, B ₹8,000.00 / ₹50,000.00, C ₹1,50,000.00 intact; clean ₹873.00; recommendation SEIZURE.
- [ ] SOP_ILL_2 shows ₹40,695.08, ₹69,446.97, ₹40,695.08, ₹24,417.05, ₹31,288.82 with "Pro-rata" badges.
- [ ] MERCHANT_200 shows ₹4,85,000.00 clean capital ring-fenced, recommendation "Targeted lien only", one overdue deadline in red.
- [ ] Impact bar shows numbers and bars; Indian comma format everywhere (₹4,85,000.00 not ₹485,000.00). When the recommendation is digital suspension, display: "Cash-hold metric only; digital-channel access impact is not quantified."
- [ ] Orders open in a sandboxed iframe; buttons stay disabled until the checkbox is ticked.
- [ ] Stop the server (Ctrl+C), refresh: page still shows data with the "Offline demo data" badge.
- [ ] Narrow the browser to phone width: still usable.
- [ ] Search your file (Ctrl+F): it contains no `http://` or `https://` anywhere, no `innerHTML` used with API data, no `eval`, no `localStorage`.
- [ ] Put a fake error into the data (ask your AI how) and confirm the yellow `errors` banner appears.

---
## WHAT YOU MUST BE ABLE TO SAY TO THE JUDGES
1. **"Walk us through the screen."** - "Top bar: how much innocent working capital a blanket freeze would lock versus our targeted approach, across the loaded cases. Below, pick a case. We show the recommendation with the SOP clauses behind it, who gets what rupee by rupee, the replay of the statement, four SOP-based deadline indicators plus one 45-day project-proposed review checkpoint, the merchant-document check, and finally draft orders the officer must sign off."
2. **"Where does the data come from?"** - "Three tiers, clearly labelled: Tier 1 contains SOP-derived worked scenarios with documented date/time normalization; Tier 2 is an invented illustrative merchant ₹200 scenario, not a verified court case; Tier 3 is synthetic, only for software stress testing."
3. **"Is any maths done in the browser?"** - "No. The browser only displays. All rupee maths and deadlines are computed on the server in deterministic Python, so the screen can't disagree with the audit trail."
4. **"What if the server or the internet dies mid-demo?"** - "The page carries a snapshot of the same results and switches to Offline demo mode automatically - and it says so on screen."
5. **"How is it secured?"** - "No external scripts, API text is inserted as plain text, and the generated orders are shown in a sandboxed frame with scripts disabled."
6. **"Who is the user?"** - "An Investigating Officer or a bank nodal officer. The tool recommends; they sign. The sign-off checkbox gates download."
7. **"Is it usable on a phone?"** - "Yes; layouts reflow and wide tables scroll inside their own box."
