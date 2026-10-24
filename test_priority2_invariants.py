"""Unit tests for Person A Priority 2 financial invariants and stress testing."""
import copy
import json
import os
import unittest

import invariants
import stress_test

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(HERE, "golden")


def _load_golden(name):
    path = os.path.join(GOLDEN, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestInvariantsAndStressTest(unittest.TestCase):
    def setUp(self):
        self.case_ill1 = _load_golden("SOP_ILL_1.case.json")
        self.attr_ill1 = _load_golden("SOP_ILL_1.attribution.json")

        self.case_ill2 = _load_golden("SOP_ILL_2.case.json")
        self.attr_ill2 = _load_golden("SOP_ILL_2.attribution.json")

        self.case_m200 = _load_golden("MERCHANT_200.case.json")
        self.attr_m200 = _load_golden("MERCHANT_200.attribution.json")

    def test_presets_pass_all_invariants(self):
        """All supported golden cases must pass 100% of conservation checks."""
        for case, attr, cid in [
            (self.case_ill1, self.attr_ill1, "SOP_ILL_1"),
            (self.case_ill2, self.attr_ill2, "SOP_ILL_2"),
            (self.case_m200, self.attr_m200, "MERCHANT_200"),
        ]:
            res = invariants.check_case_invariants(case, attr)
            self.assertTrue(res["passed"], f"Preset {cid} failed invariants: {res['errors']}")
            self.assertEqual(len(res["errors"]), 0)
            for check in res["checks"]:
                self.assertTrue(check["passed"], f"Check {check['id']} failed on {cid}")

    def test_mutated_attribution_fails_epoch_conservation(self):
        """A deliberately corrupted attribution epoch must fail EPOCH_CONSERVATION."""
        mutated_attr = copy.deepcopy(self.attr_ill1)
        # Corrupt clean balance in epoch 1
        mutated_attr["epochs"][0]["clean_balance"] = "999999.00"

        res = invariants.check_case_invariants(self.case_ill1, mutated_attr)
        self.assertFalse(res["passed"])
        failed_ids = [c["id"] for c in res["checks"] if not c["passed"]]
        self.assertIn("EPOCH_CONSERVATION", failed_ids)
        self.assertTrue(any("Epoch 1 balance mismatch" in e for e in res["errors"]))

    def test_mutated_attribution_fails_victim_disputed_conservation(self):
        """A corrupted victim hold/forwarded sum must fail VICTIM_DISPUTED_CONSERVATION."""
        mutated_attr = copy.deepcopy(self.attr_ill1)
        # Corrupt victim B's hold_in_current_account
        mutated_attr["victims"][0]["hold_in_current_account"] = "1.00"

        res = invariants.check_case_invariants(self.case_ill1, mutated_attr)
        self.assertFalse(res["passed"])
        failed_ids = [c["id"] for c in res["checks"] if not c["passed"]]
        self.assertIn("VICTIM_DISPUTED_CONSERVATION", failed_ids)

    def test_mutated_attribution_fails_negative_amount(self):
        """Negative amounts must fail NON_NEGATIVE_AMOUNTS check."""
        mutated_attr = copy.deepcopy(self.attr_ill1)
        mutated_attr["clean_ring_fenced"] = "-100.00"
        mutated_attr["epochs"][0]["clean_balance"] = "-50.00"

        res = invariants.check_case_invariants(self.case_ill1, mutated_attr)
        self.assertFalse(res["passed"])
        failed_ids = [c["id"] for c in res["checks"] if not c["passed"]]
        self.assertIn("NON_NEGATIVE_AMOUNTS", failed_ids)

    def test_stress_test_runs_and_records_counts(self):
        """Run an actual stress test and verify counts, failures structure and duration."""
        res = stress_test.run_stress_test(n=10, seed=42)
        self.assertEqual(res["requested"], 10)
        self.assertEqual(res["generated"], 10)
        self.assertEqual(res["executed"], 10)
        self.assertEqual(res["executed"], res["passed"] + res["failed"])
        self.assertEqual(len(res["failures"]), res["failed"])
        self.assertGreater(res["duration_ms"], 0)
        self.assertEqual(res["seed"], 42)

    def test_pure_function_no_mutation(self):
        """Assert check_case_invariants does not mutate inputs."""
        case_copy = copy.deepcopy(self.case_ill1)
        attr_copy = copy.deepcopy(self.attr_ill1)

        invariants.check_case_invariants(self.case_ill1, self.attr_ill1)

        self.assertEqual(self.case_ill1, case_copy)
        self.assertEqual(self.attr_ill1, attr_copy)


if __name__ == "__main__":
    unittest.main()
