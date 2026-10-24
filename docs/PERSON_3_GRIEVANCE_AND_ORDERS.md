# PERSON 3 - THE PAPERWORK ("Merchant Document Check + Draft Case Documents for Officer Review")

**You deliver 2 files:** `grievance.py` and `orders.py`.
`grievance.py` checks an innocent merchant's invoices against the disputed rows. `orders.py` writes the three draft documents an officer needs.

---
## STEP 0 - Set-up (10 minutes, once)
1. Install Python 3.11+ from python.org (Windows: tick "Add Python to PATH").
2. Unzip `mercy_ledger`, open a terminal INSIDE the folder.
3. Run `python check_my_work.py grievance` (Mac: `python3`). FAIL ("still the STUB") is correct at this point.

## STEP 1 - Copy-paste this to your AI (attach the whole folder; or paste `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md`, this file and the `golden/` files: MERCHANT_200, EXTRA_INVOICE_BAD, EXTRA_INJECTION, SOP_ILL_1, SOP_ILL_2 with `.case.json`, `.attribution.json`, `.triage.json`, `.sla.json`, `.grievance.json`, plus `orders_expectations.json`)
> You are helping build one part of a hackathon project. Read `00_RULES_FOR_EVERY_AI.md`, `01_DATA_CONTRACT.md` and `PERSON_3_GRIEVANCE_AND_ORDERS.md` completely and obey them exactly. Write the COMPLETE files `grievance.py` and `orders.py`. Copy every fixed text string from the golden files character-for-character. Reply with only the two files, each in its own code block with the file name above it. If anything is unclear, ask me instead of guessing.

## STEP 2 - Check, fix, repeat
`python check_my_work.py grievance`, then `python check_my_work.py orders`. Both must say PASS. If FAIL, paste the PROBLEMS list to your AI: "Fix exactly these, change nothing else." Then send me the two files.
**Bonus (optional, 5 min):** run `python -c "import orders,json;c=json.load(open('golden/SOP_ILL_2.case.json'));a=json.load(open('golden/SOP_ILL_2.attribution.json'));t=json.load(open('golden/SOP_ILL_2.triage.json'));s=json.load(open('golden/SOP_ILL_2.sla.json'));g=json.load(open('golden/SOP_ILL_2.grievance.json'));open('demo_order.html','w',encoding='utf-8').write(orders.build_orders(c,a,t,s,g)['restoration_order_html'])"` and double-click `demo_order.html` to see your order in the browser.

---
## `grievance.py` - `verify_grievance(case) -> dict`
Purpose: a merchant says "that disputed UPI credit was a genuine sale; here is my GST invoice". We check the invoice is **consistent** with the ledger. This is a document-vs-ledger consistency check, *not* proof of a genuine sale (the IO decides under SOP Para 10).

For **each complaint** (same order as `case["complaints"]`) produce one result:
1. Find the first invoice whose `claimed_utr == complaint["disputed_utr"]`.
2. **No invoice** -> `invoice_id: null`, all four checks `false`, `verdict: "NO_INVOICE"`, `reasons: ["No invoice submitted for this disputed UTR."]`.
3. Otherwise compute the checks:
   * `utr_match`: `true` (that's how we found it).
   * `amount_match`: `Decimal(invoice.amount) == Decimal(complaint.disputed_amount)` (exact).
   * `date_within_1_day`: find the CREDIT transaction with that UTR; `abs(invoice.date - date part of the credit's timestamp) <= 1 calendar day`. If no such credit exists -> false.
   * `gstin_format_valid`: matches the regex `^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$` (format only; we do NOT look it up in any registry - say so in the disclaimer).
4. `verdict`: `"MATCHED"` if amount, date and gstin checks are all true; else `"PARTIAL"` if `amount_match` is true; else `"NOT_MATCHED"`.
5. `reasons`: one string per failed check, in this order: `"Invoice amount differs from disputed amount."`, `"Invoice date is more than 1 day from the credit date."`, `"GSTIN is not in valid 15-character format (format check only, no registry lookup)."`. If nothing failed: `["All checks passed."]`.

Top level: `case_id`, `results`, `disputed_total` (= number of results), `disputed_matched` (= results with verdict MATCHED), `all_disputed_matched` (= `disputed_total > 0` and all matched), `disclaimer` (copy from golden).

---
## `orders.py` - `build_orders(case, attribution, triage, sla, grievance) -> dict`
Returns exactly `{"restoration_order_html", "indemnity_bond_html", "edd_packet_html"}`. Each value is a COMPLETE HTML document string (`<!DOCTYPE html><html>...`), self-contained: inline CSS only, **no JavaScript, no external links, no images**. A4-friendly (`@media print` ok).

### Hard rules (checker enforces these)
* Every document shows, prominently at the top: **`DRAFT - NOT VALID UNTIL REVIEWED AND SIGNED BY THE INVESTIGATING OFFICER`**.
* **Escape every piece of text that came from the inputs** with `html.escape(str(x), quote=True)` (holder name, victim labels, UTRs, invoice ids, narration - everything). A fraudster can type `<script>` into a field; it must come out as `&lt;script&gt;`.
* **Never calculate money here.** Only print amounts that already exist in `attribution`/`triage`/`sla`/`grievance`. No arithmetic, no LLM-written numbers.
* Format every rupee amount in **Indian grouping** with the rupee sign: `"150000.00"` -> `₹1,50,000.00`, `"873.00"` -> `₹873.00`, `"1234567.50"` -> `₹12,34,567.50`, `"0.00"` -> `₹0.00`. Write one helper `inr(s)` using string/Decimal handling (no float).
* The restoration order must contain the text `Section 106(3) BNSS`.
* Do not claim legal validity or that anything "complies" with law. Say "draft", "for officer review".

### Document 1 - `restoration_order_html`: "Restoration Order under Section 106(3) BNSS (Draft)"
Content, in this order:
1. DRAFT banner. Title. Case id, account id, account holder, as-of date.
2. **Basis** paragraph: attribution principle from SOP Para 5(xiii)(a)/(b) and Annexure-V. If the number of victims with `restorable_amount > 0` is **2 or more** cite *SOP Para 11, Process 2 (multiple victims, S.106 BNSS)*; if it is **1** cite *Process 1 (single victim, S.106(3) BNSS)*; if 0, say no money is restorable from this account.
3. **Schedule table**, one row per victim in `attribution["victims"]`: victim label, disputed amount, method (DIRECT / PRO_RATA / INTACT shown in words), **amount to restore** (`restorable_amount`), **allocated to outgoing debits** (`forwarded_downstream`, with the debit UTR(s) from `forwarded_trace`; this schema does not verify the receiving account), retention ratio when method is PRO_RATA.
4. A line: "Clean (innocent) balance outside this order: ₹X" using `clean_ring_fenced`; plus "Continuation of any restriction on this clean balance is a separate decision of the Investigating Officer (SOP Para 5(viii), 5(ix))."
5. **Instruction to bank** paragraph: remit the scheduled amounts to the victims' accounts as notified on CFCFRMS, against an indemnity bond, within **15 calendar days** of receipt of the order (SOP Para 11, Process 1(v) (single victim) / Process 2(h) (multiple victims)). Also: "Prior approval of the jurisdictional SP/DCP is required (SOP Process 1(iv))."
6. Signature block with blank lines: Investigating Officer, SP/DCP approval, Bank Nodal Officer, date.
7. Footer: "Figures computed deterministically by Mercy Ledger from the bank statement. Decision-support output; the officer retains final authority."

### Document 2 - `indemnity_bond_html`: "Indemnity Bond Schedule (Draft)"
One section per victim with `restorable_amount > 0` (if none, one line saying so): victim label, amount, and a **template undertaking** with blanks to fill: the recipient undertakes to produce the amount before the court as and when required and to give effect to the further orders of the jurisdictional court as to its disposal (this follows SOP Process 1(iv)/Process 2). Add: "Template wording to be vetted by the prosecuting/legal team before use." Signature + witness lines.

### Document 3 - `edd_packet_html`: "7-Day Bank EDD Clearance Packet (Draft)"
1. DRAFT banner, title, case/account/holder.
2. **Deadline box**: the `BANK_GRIEVANCE_7D` clock from `sla` (label, deadline, status, days left; "Not started" if NOT_STARTED) and its `sop_reference`.
3. **Document verification table** from `grievance["results"]`: complaint id, disputed UTR, disputed amount, invoice id (or "-"), the four checks as Yes/No, verdict, reasons. Under it, the grievance `disclaimer`.
4. **Recommendation** from `triage`: recommendation in words, score, rationale, and each citation as a list item. Say "human sign-off required".
5. Signature lines: Bank Nodal Officer, Date.

Use plain, readable CSS (a table, a coloured status chip). Keep each document under ~15 KB.

---
## FORBIDDEN
`float(`, `<script`, any JavaScript in output, `datetime.now`, `date.today`, any network/AI library, un-escaped input text, arithmetic on rupee amounts inside orders.py, editing inputs, extra keys.

## WHAT YOU MUST BE ABLE TO SAY TO THE JUDGES
1. **"Do you use an LLM to write the legal orders?"** - "No. The orders are fixed templates. The only things we insert are numbers already computed by our deterministic engine, and all inserted text is HTML-escaped. So the AI-hallucinated-rupee-amount problem and the prompt-injection problem both disappear by design."
2. **"What if a fraudster puts malicious text inside an invoice?"** - "Invoices are structured fields, not free text for an AI to read. Everything printed is escaped, and the checker has a test with `<script>` in the account-holder name."
3. **"Do you read invoice PDFs?"** - "Not in this version - invoice data is entered as structured fields (id, date, amount, GSTIN, UTR). Reading PDFs/photos would be added as a schema-constrained extraction step whose output is still verified by the same deterministic checker. We chose not to ship a half-working extractor."
4. **"Does matching an invoice prove the merchant is innocent?"** - "No. It's a consistency check between the document and the ledger row, plus a GSTIN *format* check (no registry lookup). It supports the grievance; the IO verifies and decides under SOP Para 10."
5. **"Is the order legally valid?"** - "It's a draft for officer review, marked as such on every page. It follows the SOP's process (Para 11 Process 1/2: S.106(3) BNSS, indemnity bond, SP/DCP approval, 15 days). Legal wording should be vetted by the prosecution/legal team - we say that in the document."
6. **"What about the indemnity bond?"** - "SOP Process 1(iv) requires the victim to execute an indemnity bond undertaking to produce the amount before the court on demand. We generate the schedule and a template; signing is the officer's and victim's job."
7. **"Why Indian number format?"** - "Officers read ₹1,50,000 not ₹150,000; it's done with string handling, not floats, so no rounding drift."
