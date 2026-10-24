"""Unit tests for Person C Priority 2 plain-language victim explanation generator."""
import copy
import json
import os
import unittest

from victim_explainer import explain_victims

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(HERE, "golden")


def _load_golden(name):
    path = os.path.join(GOLDEN, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestVictimExplainer(unittest.TestCase):
    def setUp(self):
        self.case_ill1 = _load_golden("SOP_ILL_1.case.json")
        self.attr_ill1 = _load_golden("SOP_ILL_1.attribution.json")

        self.case_ill2 = _load_golden("SOP_ILL_2.case.json")
        self.attr_ill2 = _load_golden("SOP_ILL_2.attribution.json")

        self.case_m200 = _load_golden("MERCHANT_200.case.json")
        self.attr_m200 = _load_golden("MERCHANT_200.attribution.json")

    def test_victim_with_zero_remaining_and_forwarded(self):
        """Test explanation for Victim A in SOP_ILL_1 (0 remaining, 97000 forwarded)."""
        res = explain_victims(self.case_ill1, self.attr_ill1)
        exp_a = next(e for e in res["explanations"] if e["complaint_id"] == "A")
        self.assertEqual(exp_a["restorable_amount"], "0.00")
        self.assertEqual(exp_a["forwarded_downstream"], "97000.00")
        self.assertIn("reports no amount remaining attributable", exp_a["plain_explanation"])
        self.assertIn("destination account is not verified", exp_a["limitation"])
        # Must not claim the victim can never recover
        self.assertNotIn("never recover", exp_a["plain_explanation"].lower())

    def test_victim_with_partial_funds_remaining(self):
        """Test explanation for Victim B in SOP_ILL_1 (8000 remaining, 50000 forwarded)."""
        res = explain_victims(self.case_ill1, self.attr_ill1)
        exp_b = next(e for e in res["explanations"] if e["complaint_id"] == "B")
        self.assertEqual(exp_b["restorable_amount"], "8000.00")
        self.assertEqual(exp_b["forwarded_downstream"], "50000.00")
        self.assertIn("remaining-attributed in this account", exp_b["plain_explanation"])
        self.assertIn("not a decision to release funds", exp_b["plain_explanation"])
        self.assertIn("destination account is not verified", exp_b["limitation"])

    def test_victim_with_full_intact_funds(self):
        """Test explanation for Victim C in SOP_ILL_1 (150000 intact)."""
        res = explain_victims(self.case_ill1, self.attr_ill1)
        exp_c = next(e for e in res["explanations"] if e["complaint_id"] == "C")
        self.assertEqual(exp_c["restorable_amount"], "150000.00")
        self.assertEqual(exp_c["forwarded_downstream"], "0.00")
        self.assertEqual(exp_c["attribution_method"], "INTACT")
        self.assertIn("remained fully intact", exp_c["plain_explanation"])
        self.assertIn("not a decision to release funds", exp_c["plain_explanation"])

    def test_multiple_victims_preserve_order(self):
        """Test multiple victims in SOP_ILL_2 preserving exact order."""
        res = explain_victims(self.case_ill2, self.attr_ill2)
        self.assertEqual(len(res["explanations"]), 5)
        ids = [e["complaint_id"] for e in res["explanations"]]
        expected_ids = [v["complaint_id"] for v in self.attr_ill2["victims"]]
        self.assertEqual(ids, expected_ids)

    def test_deterministic_output(self):
        """Assert identical inputs produce identical output."""
        res1 = explain_victims(self.case_ill1, self.attr_ill1)
        res2 = explain_victims(self.case_ill1, self.attr_ill1)
        self.assertEqual(json.dumps(res1, sort_keys=True), json.dumps(res2, sort_keys=True))

    def test_absence_of_unsupported_recovery_or_guilt_claims(self):
        """Verify explanations never declare guilt or claim verified fund recovery."""
        for case, attr in [(self.case_ill1, self.attr_ill1), (self.case_ill2, self.attr_ill2), (self.case_m200, self.attr_m200)]:
            res = explain_victims(case, attr)
            all_text = [res["disclaimer"]]
            for exp in res["explanations"]:
                all_text.append(exp["plain_explanation"])
                all_text.append(exp["limitation"])

            combined = " ".join(all_text).lower()
            for forbidden in ["guilty", "criminal", "fraudster", "funds were restored", "recovered funds", "guarantee"]:
                self.assertNotIn(forbidden, combined, f"Forbidden term '{forbidden}' found in explanation")


if __name__ == "__main__":
    unittest.main()
