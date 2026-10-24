# Mercy Ledger: Explainable Cyber-Fraud Fund Reconciliation and Proportionate Restriction Decision Support

**Project type:** FinTech / RegTech hackathon prototype  
**Primary users:** Investigating officers, bank nodal officers, and authorized case reviewers  
**Regulatory reference:** Ministry of Home Affairs / Indian Cyber Crime Coordination Centre (I4C), *SOP for NCRP-CFCFRMS, Custody, Restoration of Money and Grievance Redressal* (dated 2 January 2026), used as a reference for applicable workflows and selected worked examples.

## 1. Problem Statement

Cyber-enabled financial fraud investigations can involve multiple victims, several beneficiary accounts, partial withdrawals, onward transfers, and account balances that combine disputed inflows with legitimate funds. After a complaint is reported and relevant transactions are identified, investigators and financial institutions may need to reconcile bank statements with complaint records, establish how much can reasonably be attributed to each victim, identify amounts that have moved onwards, and assess the potential financial consequences of different account-restriction scenarios.

This work can be difficult to reproduce and explain when it relies on manual spreadsheet calculations. It is also possible to overstate what the records establish: a transaction link does not by itself prove criminal intent; a debit does not necessarily identify the destination account; and a balance not currently attributed by a calculation is not automatically legally cleared. When several complaints point to the same account or pool of funds, overlapping claims and double-counting can further complicate reconciliation.

**Mercy Ledger** is an explainable cyber-fraud fund-reconciliation and decision-support prototype designed to turn supported bank-statement records, structured complaint data, and relevant case details into an auditable financial analysis. It applies documented chronological attribution rules where the supplied records support them, computes pro-rata allocations in applicable commingled-fund scenarios, checks financial consistency, and explains how each displayed amount was produced. It also provides a controlled view of linked transactions across multiple supplied account records, compares hypothetical account-restriction scenarios, and produces neutral case summaries for review by an authorized person.

The prototype is intended to complement—not replace—existing cybercrime reporting, financial-institution, and law-enforcement processes. It does not claim to replace NCRP/CFCFRMS or other existing systems, determine guilt, authorize a freeze or release, or guarantee recovery of victims' money. Its contribution is the reproducibility, transparency, and reviewability of the analysis performed on the records supplied to it.

## 2. Main Objective

Develop a Python-based application that helps an authorized reviewer understand disputed-fund calculations and their potential account impact through deterministic arithmetic, visible transaction evidence, explicit assumptions, and human-reviewed reports.

The prototype will emphasize five properties:

1. **Explainability:** Every important result should identify the transaction rows, inputs, and rules or assumptions used to produce it.
2. **Financial consistency:** Balances, attributed amounts, outflows, and allocations should reconcile under documented calculation rules and tolerances.
3. **No double-counting:** The same principal must not be represented as independently available in multiple accounts simply because it moved through successive transactions.
4. **Explicit uncertainty:** Missing identifiers, ambiguous transaction matches, unsupported data, and assumptions that materially affect an outcome must be visible and must not be turned into false certainty.
5. **Proportionate human review:** The system may compare financial consequences and surface review indicators, but only an appropriately authorized person can decide what legal action is warranted.

## 3. Proposed Prototype Capabilities

### 3.1 Case input and validation

Accept a supported bank-statement CSV, structured complaint records, and relevant case information. Validate required fields, timestamps, debit/credit direction, amounts, transaction identifiers, duplicates where detectable, and statement-balance consistency. Show clear errors or warnings when records are missing, inconsistent, or outside the supported format.

### 3.2 Chronological fund attribution

Process transactions in a defined order and apply the implemented attribution rules to supported cases where the supplied history permits a reasonable calculation. Display the relevant credits, subsequent debits, remaining attributed amount, and amounts associated with outgoing transactions. Use financial decimal arithmetic and documented precision/rounding rules.

The selected worked examples from Annexure V of the SOP will be used as reference test cases. Implemented behaviour must be described accurately: the program should not imply that one debit-consumption assumption is a universal statutory algorithm unless the governing source explicitly establishes that rule.

### 3.3 Pro-rata allocation for applicable commingled-fund cases

Where the applicable scenario and available records do not permit reasonable individual attribution because funds have been commingled, calculate proportional allocations using the documented eligible pool and allocation weights. Display the formula, inputs, rounding, and reconciliation result. The system must not apply pro-rata allocation indiscriminately to cases where direct attribution is supported.

### 3.4 Financial-conservation and invariant checks

Run explicit checks on the analysis output, such as:

- Opening balance + credits − debits = calculated closing balance, where the required fields are present.
- Replay balances agree with the transaction sequence and statement values within the documented tolerance.
- Clean/unattributed balance plus the remaining attributed pool reconciles with the account balance under the selected model.
- Attributed amounts reconcile with remaining attributed amounts and amounts assigned to outflows under the defined accounting model.
- Victim allocations do not exceed the eligible available pool, and overlapping claims are surfaced for review rather than silently allocated twice.
- Provisional hold totals and attribution-derived totals are shown separately where they represent different concepts.

These checks measure software and accounting consistency. They do not measure real-world fraud-detection accuracy or establish a legal entitlement to money.

### 3.5 Controlled multi-account transaction-link view

For a separate, clearly labelled synthetic or explicitly supported multi-account dataset, match candidate debit/credit records using supplied transaction references (such as UTR), amounts, timestamps, and available counterparty identifiers. Visualize accounts as nodes and corroborated or candidate transfers as directed edges. Allow the reviewer to inspect the records behind a link and show matched, ambiguous, unmatched, or invalid records distinctly.

The initial enhancement is a **transaction-link graph**, not a complete per-rupee multi-hop provenance engine. A matching transfer reference and amount can support a record-level link, but does not prove who controlled an account, establish criminal intent, or prove that the same money remained individually identifiable after commingling. Full multi-hop attribution through splits, partial debits, mixed pools, loops, and downstream accounts is outside the initial prototype unless separately implemented and validated.

### 3.6 Assumption sensitivity analysis

Where debit-consumption assumptions are not established as one universal rule for every scenario, compare clearly labelled analytical hypotheses—for example, disputed-funds-first, proportional consumption, and clean-funds-first. Show the resulting attributed amounts, allocated outflows, and clean/unattributed balance side by side, and allow the reviewer to inspect the transactions that cause differences.

These are sensitivity scenarios, not automatically SOP-approved legal methods. The primary configured model and its tests remain distinct from the alternatives. The outcome range must not be described as a guaranteed or legally determined “restorable amount.”

### 3.7 Account-restriction impact comparison

Present three illustrative decision-support scenarios using the same underlying case data:

- **Broad restriction scenario:** show the full account balance potentially affected under the stated hypothetical.
- **Amount-limited scenario:** show the disputed amount currently supported by the model and the other balance not currently attributed by it.
- **Further-review scenario:** show why ambiguous links, incomplete records, competing claims, or unresolved assumptions prevent a more confident comparison.

The interface must distinguish a monetary hold/lien, suspension of digital banking services, and seizure as different legal and operational measures. It must not instruct a bank to freeze or release funds. An amount described as “not currently attributed” is not automatically innocent, unencumbered, or legally cleared.

### 3.8 Merchant evidence matching and case comparison

Compare structured evidence fields—such as invoice identifier, date, amount, UTR, and delivery indicator—with the relevant disputed transaction. Include at least two labelled demonstration cases where available: one with structured evidence that matches, and one with evidence that fails to match or remains incomplete. Describe results as matches, mismatches, or unresolved evidence, not automatic findings of innocence or guilt.

Automated extraction from arbitrary invoice PDFs or images is outside the initial prototype.

### 3.9 Interactive transaction replay

Provide a step-by-step replay of the selected single-account case. At each step, show the transaction, account balance under the model, remaining attributed pool, relevant outflow allocation, and warnings. Link each displayed result back to the underlying transaction row. Replay must use actual backend analysis data, not a separate set of hardcoded display numbers.

### 3.10 Plain-language victim explanation

Generate a neutral, template-based explanation for each complaint or victim, summarizing the reported amount, amount remaining attributed under the configured model, amounts assigned to outflows, calculation method, and relevant limitations. If a destination account cannot be identified from the supplied data, state that explicitly. Do not claim that money has been recovered unless the case data contains a verified restoration status.

### 3.11 Audit fingerprint and report verification

Create a SHA-256 fingerprint from a canonical representation of the case inputs, engine version, and analysis output. Add a re-verification action that recomputes the fingerprint and reports whether the current payload matches the recorded digest.

The fingerprint is an integrity aid, not proof that source documents are authentic, that the calculations are legally correct, who authored the report, or that a report is admissible in court. A digest stored alongside an editable report can be replaced by someone who edits both; stronger assurance would require protected storage or an appropriate digital-signature process.

### 3.12 Stress-test panel and auditable draft report

Run the attribution function against actual fixed test cases and, when available, deterministic generated synthetic cases. Show the actual case count, random seed if used, passed/failed invariant checks, and details of failures. Never present hardcoded success counts as test results. Synthetic testing demonstrates implementation behaviour, not accuracy on real investigations.

Generate a draft case report containing inputs considered, transaction references, calculation steps, allocations, restriction scenarios, warnings, evidence matches, unresolved links, model assumptions, audit fingerprint, and proposed next steps for authorized review.

## 4. Judge-Facing Interface and Demonstration

The dashboard should prioritize legibility and explainability rather than decorative visualizations. It should include:

1. **Case header:** case identifier, data source, and a visible “Synthetic demo data” label for simulated cases.
2. **Summary cards:** reported disputed amount, amount remaining attributed under the model, amount associated with outgoing debits, and balance not currently attributed by the model.
3. **Transaction replay:** an interactive timeline/stepper for the selected case.
4. **Transfer-link view:** a controlled multi-account graph with link-status labels and an evidence-details panel.
5. **Restriction comparison:** broad, amount-limited, and further-review scenario cards with clear assumptions.
6. **Integrity and test panel:** actual invariant and stress-test outcomes, plus the report fingerprint and re-verification result.
7. **Evidence and uncertainty panel:** matching documents, mismatches, missing identifiers, and unresolved links.
8. **Victim explanation and report:** plain-language output plus a detailed, exportable draft report where implemented.

Use a restrained, professional financial-investigation design: consistent spacing, readable tables, clear currency formatting, meaningful status labels, accessible contrast, responsive layouts, loading and error states, and visible distinctions between verified facts, candidate links, assumptions, and unavailable information. Green/amber/red status colors must also have text or icons so the result is not communicated by color alone.

## 5. Evaluation and Success Criteria

The prototype is ready to demonstrate when the team can verify the following against the actual running application:

1. Selected Annexure V worked scenarios produce the expected results in automated tests.
2. Supported case inputs are validated and invalid or incomplete records produce clear messages.
3. Calculations and allocations reconcile under documented rules and rounding tolerances.
4. Overlapping claims or allocations that exceed the eligible pool are detected by explicit checks.
5. Candidate multi-account links are based on supplied records and are labelled accurately; ambiguous or unmatched links are not invented.
6. Alternative sensitivity assumptions are clearly labelled and show their impact on the same case.
7. Restriction-impact figures are derived from actual backend results and are not presented as legal decisions.
8. Replay, explainers, report outputs, and the dashboard agree with the same underlying analysis.
9. Audit fingerprint verification detects a changed canonical input/output payload relative to a saved digest.
10. Stress-test counts reflect cases actually executed and checked.
11. The full demo starts reliably from a clean environment using clearly labelled sample data.

Any numerical performance or accuracy claim should be made only after it has been measured and documented. Synthetic cases must not be presented as evidence of production performance.

## 6. Out of Scope for the Initial Prototype

- Live integration with banks, NCRP, CFCFRMS, payment networks, or law-enforcement systems.
- Comprehensive cross-bank or cross-border tracing and confirmed per-rupee lineage through every hop.
- Access to non-public bank records, beneficial-ownership databases, or foreign account information unless explicitly supplied through an authorized dataset.
- Automated OCR/extraction from arbitrary invoices or PDFs.
- Production-grade authentication, access controls, security certification, deployment, or operational use on real investigations.
- Automatically issuing legally operative orders, declaring accounts innocent or guilty, or authorizing account restrictions and fund releases.
- Claims that a hash alone proves authenticity, authorship, legal admissibility, or correctness.

## 7. Guiding Principles

- **Deterministic arithmetic:** monetary calculations are performed in tested code using appropriate decimal arithmetic.
- **Traceability:** every important result should link to its input records and calculation path.
- **Conservation:** allocations and balances should reconcile under the chosen model, with tolerance and rounding documented.
- **No fabricated certainty:** missing counterparty details, ambiguous links, and unverified evidence remain explicit limitations.
- **Separation of concepts:** reported amounts, current attributed amounts, amounts sent onwards, provisional holds, and confirmed restored amounts must not be conflated.
- **Proportionality:** show financial consequences without automatically labelling non-attributed balances as legally cleared.
- **Human oversight:** the application supports review; authorized officers and competent legal authorities retain decision-making responsibility.
- **Regulatory accuracy:** cite the relevant SOP workflow and trigger conditions. Keep project assumptions and analytical sensitivity modes separate from SOP requirements.
- **Honest demonstration:** distinguish implemented functionality, synthetic demonstration functionality, and future roadmap items.

## 8. Project Contribution

Mercy Ledger's proposed contribution is an explainable reconciliation workflow that combines supported victim-level fund attribution, explicit conservation and overlap checks, controlled transaction-link visualization, assumption sensitivity, restriction-impact comparisons, and auditable case explanations. The project does not claim that transaction tracing or restoration is new in itself, nor that its prototype replaces existing Indian cybercrime systems. It aims to demonstrate how financial calculations can be made easier to inspect, reproduce, and challenge during case review.

## 9. Concise Pitch

> **Mercy Ledger is an explainable cyber-fraud fund-reconciliation and proportionate-restriction decision-support prototype. It analyzes supported statement and complaint records, calculates victim-level attribution and applicable pro-rata allocations, checks financial consistency and overlapping claims, visualizes candidate transaction links across supplied account records, and compares hypothetical restriction scenarios. Each result is accompanied by transaction-level reasoning, explicit uncertainty, and an auditable draft report for human review.**

*This document describes the proposed enhanced hackathon prototype. It is not legal advice and does not establish that the software is suitable for operational use in banks or law-enforcement investigations. Each feature should be described as implemented only after it is integrated and verified in the running application.*
