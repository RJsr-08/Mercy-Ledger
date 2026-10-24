# COPY/PASTE PROMPT — PERSON C, PRIORITY 3

You are **Person C — Report Integrity Fingerprint Owner**. Only start after Priority 1 and 2 pass. Read the report shapes from `orders.py`, `01_DATA_CONTRACT.md` and the current Python style rules first.

## Create only

- `audit_integrity.py`
- `test_priority3_audit_integrity.py`

Do not edit `orders.py`, `attribution.py`, `pipeline.py`, `app.py`, golden files or the checker.

## Required interface

Implement:

- `create_fingerprint(case, engine_version, analysis_output) -> dict`
- `verify_fingerprint(case, engine_version, analysis_output, expected_digest) -> dict`

Use only standard-library `json` and `hashlib`. Compute SHA-256 over canonical JSON of a defined envelope containing case input, explicit engine version and analysis output. Use stable serialization such as sorted keys, fixed separators and UTF-8. Avoid non-JSON values and ensure the same semantic data is serialized consistently.

Fingerprint output should contain algorithm, digest, engine version and an explanation of what was hashed. Verification returns a boolean plus concise details; one changed input or output should cause a mismatch. Never embed secrets. Do not read/write files, get the system clock, or make network calls in this helper.

The disclaimer must state that a digest is only a tamper-detection aid relative to a known expected digest; it does not prove original data authenticity, author identity, legal correctness or admissibility. If both report and digest can be edited, the digest can be replaced too; protected storage or digital signatures would be needed for stronger assurances.

## Tests

Use `unittest` to verify determinism, changed input, changed output, changed engine version, bad digest and JSON-safe output. Do not call it a digital signature.

## Handoff

Run `python -m unittest test_priority3_audit_integrity.py`. Send only `audit_integrity.py`, the test file, actual output and known limitations.
