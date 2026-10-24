"""Unit tests for Person C Priority 3 report integrity fingerprinting."""
import copy
import json
import os
import unittest

from audit_integrity import create_fingerprint, verify_fingerprint

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(HERE, "golden")


def _load_golden(name):
    path = os.path.join(GOLDEN, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestAuditIntegrity(unittest.TestCase):
    def setUp(self):
        self.case = _load_golden("SOP_ILL_1.case.json")
        self.output = _load_golden("SOP_ILL_1.attribution.json")
        self.version = "1.0.0"

    def test_deterministic_digest(self):
        """Same input and output produces the exact same digest every time."""
        fp1 = create_fingerprint(self.case, self.version, self.output)
        fp2 = create_fingerprint(self.case, self.version, self.output)
        self.assertEqual(fp1["digest"], fp2["digest"])
        self.assertEqual(len(fp1["digest"]), 64)

    def test_successful_verification(self):
        """Expected digest correctly verifies as valid."""
        fp = create_fingerprint(self.case, self.version, self.output)
        res = verify_fingerprint(self.case, self.version, self.output, fp["digest"])
        self.assertTrue(res["valid"])
        self.assertEqual(res["calculated_digest"], fp["digest"])

    def test_changed_input_causes_mismatch(self):
        """A single character change in case input must invalidate the digest."""
        fp = create_fingerprint(self.case, self.version, self.output)
        mutated_case = copy.deepcopy(self.case)
        mutated_case["opening_balance"] = "874.00"

        res = verify_fingerprint(mutated_case, self.version, self.output, fp["digest"])
        self.assertFalse(res["valid"])
        self.assertIn("Integrity check failed", res["details"])

    def test_changed_output_causes_mismatch(self):
        """A change in analysis output must invalidate the digest."""
        fp = create_fingerprint(self.case, self.version, self.output)
        mutated_output = copy.deepcopy(self.output)
        mutated_output["clean_ring_fenced"] = "874.00"

        res = verify_fingerprint(self.case, self.version, mutated_output, fp["digest"])
        self.assertFalse(res["valid"])

    def test_changed_engine_version_causes_mismatch(self):
        """A change in engine version must change the digest."""
        fp1 = create_fingerprint(self.case, "1.0.0", self.output)
        fp2 = create_fingerprint(self.case, "1.0.1", self.output)
        self.assertNotEqual(fp1["digest"], fp2["digest"])

    def test_bad_digest_fails_cleanly(self):
        """Malformed or completely different digest fails verification gracefully."""
        res = verify_fingerprint(self.case, self.version, self.output, "bad_digest_string")
        self.assertFalse(res["valid"])

    def test_disclaimer_avoids_digital_signature_claims(self):
        """Ensure disclaimer clearly disclaims digital signatures and admissibility."""
        fp = create_fingerprint(self.case, self.version, self.output)
        self.assertIn("tamper-detection aid", fp["disclaimer"])
        self.assertNotIn("digital signature", fp["explanation"].lower())


if __name__ == "__main__":
    unittest.main()
