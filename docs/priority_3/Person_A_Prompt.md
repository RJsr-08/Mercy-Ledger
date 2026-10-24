# COPY/PASTE PROMPT — PERSON A, PRIORITY 3

You are **Person A — Controlled Multi-Account Link Graph Owner**. Only begin after Priority 1 and 2 pass. Read `01_DATA_CONTRACT.md`, `attribution.py`, `invariants.py`, the current transaction schema and the limitations in this prompt.

## Create only

- `chain.py`
- `test_priority3_chain.py`

Do not edit `attribution.py`, `presets.py`, `pipeline.py`, `app.py`, existing modules, checker or golden fixtures.

## Purpose

Create a standalone, deterministic graph/link exploration helper for a **controlled synthetic multi-account dataset**. It visualizes supplied evidence; it is not a production tracing system and must not assert exact per-rupee lineage after arbitrary commingling.

## Interface

Implement `trace_chains(dataset) -> dict`. Document an input schema containing account records and transactions with at least `account_id`, `txn_id`, timestamp, direction (`DEBIT`/`CREDIT`), amount string, and available transaction/counterparty identifiers. Prefer an explicit shared `transfer_id` or reciprocal transaction references to match a sender debit to a receiver credit. Use a transaction UTR and amount as a candidate match only when the available identifying information is insufficient to confirm the link.

Return JSON-safe `nodes`, `edges`, `paths` and `warnings`. Each edge must show match status (`VERIFIED_LINK`, `CANDIDATE_LINK`, or `UNRESOLVED`), source/target account if known, amount and the evidence fields used. If a destination is not in the supplied data, do not invent it. If multiple recipient rows match, label ambiguous and do not choose one silently.

Use `Decimal` for amount comparisons; output money strings. Enforce timestamp order where meaningful. Prevent cycles or duplicate edge traversal from inflating any aggregate; a repeated transfer is another event, but not newly created principal. Avoid calling `attribution.py` with altered input or claiming the graph itself determines legal ownership or guilt.

Include a small deterministic synthetic example helper only if needed by tests; all such data must be labelled synthetic. Use only the standard library.

## Tests

Test: verified debit/credit pair; UTR-only candidate; no matching credit; ambiguous duplicate matches; repeated hop; split transfers; missing destination; deterministic output; and principal not doubled by counting identical value at successive hops.

## Handoff

Run `python -m unittest test_priority3_chain.py`. Send only the two files, actual output and exact limitations. If a robust implementation requires changing existing schemas or the core attribution algorithm, stop and report the dependency rather than touching the protected files.
