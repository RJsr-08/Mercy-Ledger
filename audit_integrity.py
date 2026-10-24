"""Audit integrity fingerprint and tamper-detection engine for Mercy Ledger.

Implements UNODC and statutory evidentiary chain-of-custody standards by computing
and verifying deterministic SHA-256 digests over canonical JSON payloads
combining case input data, engine version, and analysis outputs.
"""
import hashlib
import json

ALGORITHM = "SHA-256"

DISCLAIMER = (
    "A cryptographic digest is a mathematical tamper-detection aid relative to a known "
    "expected digest. It does not prove original data authenticity, author identity, "
    "legal correctness, or judicial admissibility. If both the report payload and digest "
    "can be modified, independent secure storage or digital certificates are required."
)


def _canonical_json_bytes(envelope):
    """Serialize a Python dictionary to canonical, deterministic UTF-8 JSON bytes."""
    return json.dumps(
        envelope,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def create_fingerprint(case, engine_version, analysis_output):
    """Compute a deterministic SHA-256 audit digest for a case and its analysis output.

    Args:
        case: dict containing case input.
        engine_version: str specifying the analysis engine release/version.
        analysis_output: dict containing pipeline analysis results.

    Returns:
        dict with algorithm, digest, engine_version, envelope_bytes, explanation, and disclaimer.
    """
    envelope = {
        "case": case,
        "engine_version": str(engine_version),
        "analysis_output": analysis_output,
    }
    payload_bytes = _canonical_json_bytes(envelope)
    digest = hashlib.sha256(payload_bytes).hexdigest()

    return {
        "algorithm": ALGORITHM,
        "digest": digest,
        "engine_version": str(engine_version),
        "envelope_bytes": len(payload_bytes),
        "explanation": (
            "SHA-256 hash computed over canonical JSON envelope containing case records, "
            "engine version identifier, and full analysis results."
        ),
        "disclaimer": DISCLAIMER,
    }


def verify_fingerprint(case, engine_version, analysis_output, expected_digest):
    """Verify whether a payload matches a known expected SHA-256 audit digest.

    Args:
        case: dict containing case input.
        engine_version: str specifying the analysis engine release/version.
        analysis_output: dict containing pipeline analysis results.
        expected_digest: str, the reference SHA-256 hexadecimal digest.

    Returns:
        dict with valid (bool), calculated_digest, expected_digest, details, and disclaimer.
    """
    computed = create_fingerprint(case, engine_version, analysis_output)
    calc_digest = computed["digest"]

    clean_expected = str(expected_digest or "").strip().lower()
    is_valid = (calc_digest == clean_expected)

    if is_valid:
        details = "Integrity verified: calculated digest exactly matches expected digest."
    else:
        details = (
            f"Integrity check failed: digest mismatch. "
            f"Calculated {calc_digest[:16]}... vs Expected {clean_expected[:16]}..."
        )

    return {
        "valid": is_valid,
        "calculated_digest": calc_digest,
        "expected_digest": clean_expected,
        "algorithm": ALGORITHM,
        "engine_version": str(engine_version),
        "details": details,
        "disclaimer": DISCLAIMER,
    }
