# Mercy Ledger Documentation Index

This directory centralizes all design specifications, prompt histories, technical reports, and authoritative reference documents for the Mercy Ledger project.

---

## 🏛️ Authoritative Reference Pillars

- **[`REFERENCES.md`](REFERENCES.md)**: **The Complete Authoritative Reference Matrix**:
  1. **BPR&D (Bureau of Police Research & Development, MHA)**: *Challenges in Tracing Money Trail in Cyber Fraud and Way Forward* (Multi-hop mule tracking, rapid UPI/IMPS layering, targeted lien vs. blunt S.91/S.94 freezing).
  2. **RBI (Reserve Bank of India)**: *Master Directions on Fraud Risk Management, 2024* (Automated Transaction Monitoring Systems, mule account governance, velocity controls, avoiding unwarranted denial of service).
  3. **IIBF & NFSU**: *Red Flags and Hidden Trails: Forensic Accounting in Asset Tracing and Cyber Fraud* (Dr. Himanshu D. Thakkar & Saptarshi Datta, *BankQuest* 2025; Clayton's FIFO, Hallett's estate, LIBR, and pro-rata equitable restitution).
  4. **UNODC & StAR**: *Financial Investigation and Asset Tracing Guide* (International proportionality in provisional restraint, protection of bona fide third parties, and cryptographic chain of custody).
  5. **MHA / I4C**: *Standard Operating Procedure for NCRP-CFCFRMS, Custody, Restoration & Grievance Redressal* (2 January 2026; [`../references/SOP_NCRP_CFCFRMS_2026-01-02.pdf`](../references/SOP_NCRP_CFCFRMS_2026-01-02.pdf)).

---

## 📑 Core Specifications & System Rules

- **[`00_RULES_FOR_EVERY_AI.md`](00_RULES_FOR_EVERY_AI.md)**: Foundational engineering rules: strict deterministic computation, `Decimal` currency handling, immutable inputs, and no system clock dependency.
- **[`01_DATA_CONTRACT.md`](01_DATA_CONTRACT.md)**: JSON schemas, keys, units, and mathematical definitions shared across all 4 developer roles.
- **[`JUDGE_QA_MASTER.md`](JUDGE_QA_MASTER.md)**: Master question-and-answer guide for hackathon judges covering legal basis, accounting mechanics, and architecture.
- **[`INTEGRATION_PROTOCOL.md`](INTEGRATION_PROTOCOL.md)**: Four-person team git workflow, interface contracts, and integration criteria.
- **[`ROLE_AND_PRIORITY_MAP.md`](ROLE_AND_PRIORITY_MAP.md)**: Complete mapping of team responsibilities across Priority 1, 2, and 3.
- **[`START_HERE.md`](START_HERE.md)** & **[`README_START_HERE.md`](README_START_HERE.md)**: Initial orientation guide for contributors.
- **[`ADDITIONAL_FEATURES_REFERENCE.md`](ADDITIONAL_FEATURES_REFERENCE.md)**: Deep-dive references into stretch capabilities and multi-account models.
- **[`MERCY_LEDGER_UPDATED_PROBLEM_STATEMENT_V2.md`](MERCY_LEDGER_UPDATED_PROBLEM_STATEMENT_V2.md)**: Full challenge problem statement and context.

---

## 📄 Technical Reports

- **[`Mercy_Ledger_Technical_Report_v2.pdf`](Mercy_Ledger_Technical_Report_v2.pdf)**: Detailed technical whitepaper (v2) detailing mathematical formulations, regulatory compliance, and benchmark results.
- **[`Mercy_Ledger_Technical_Report.pdf`](Mercy_Ledger_Technical_Report.pdf)**: Technical whitepaper (v1).

---

## 👥 Role Specifications

- **[`PERSON_1_ATTRIBUTION_ENGINE.md`](PERSON_1_ATTRIBUTION_ENGINE.md)**: Person A specifications (Attribution, Invariants, Simulator).
- **[`PERSON_2_TRIAGE_SLA_IMPACT.md`](PERSON_2_TRIAGE_SLA_IMPACT.md)**: Person B specifications (Triage, Deadlines, Impact, Sensitivity).
- **[`PERSON_3_GRIEVANCE_AND_ORDERS.md`](PERSON_3_GRIEVANCE_AND_ORDERS.md)**: Person C specifications (Grievance, S.106 Orders, Explainers, Audit).
- **[`PERSON_4_FRONTEND.md`](PERSON_4_FRONTEND.md)**: Person D specifications (Pipeline, FastAPI backend, Interactive UI).

---

## 🎯 Priority Sprint Prompts & Acceptance Gates

- **[`priority_1/`](priority_1/)**: Core MVP Prompts & Acceptance Gates (Priority 1).
- **[`priority_2/`](priority_2/)**: Judge-Visible Depth Prompts & Acceptance Gates (Priority 2).
- **[`priority_3/`](priority_3/)**: Stretch Feature Prompts & Acceptance Gates (Priority 3).
