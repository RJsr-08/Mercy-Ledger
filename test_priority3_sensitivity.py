"""Unit tests for Priority 3 attribution assumption sensitivity analysis."""
import copy
import json
import os
import unittest
from decimal import Decimal

from sensitivity import analyze_sensitivity

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(HERE, "golden")


def _load_golden(name):
    path = os.path.join(GOLDEN, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestSensitivityAnalysis(unittest.TestCase):
    def setUp(self):
        self.case_ill1 = _load_golden("SOP_ILL_1.case.json")
        self.attr_ill1 = _load_golden("SOP_ILL_1.attribution.json")

        self.case_ill2 = _load_golden("SOP_ILL_2.case.json")
        self.attr_ill2 = _load_golden("SOP_ILL_2.attribution.json")

        self.case_m200 = _load_golden("MERCHANT_200.case.json")
        self.attr_m200 = _load_golden("MERCHANT_200.attribution.json")

        self.controlled_case = {
            "case_id": "CONTROLLED_SENSITIVITY_01",
            "opening_balance": "10000.00",
            "complaints": [
                {
                    "complaint_id": "V1",
                    "victim_label": "Victim 1",
                    "disputed_utr": "UTR-V1",
                    "disputed_amount": "20000.00",
                    "complaint_timestamp": "2026-01-01T12:00:00",
                }
            ],
            "transactions": [
                {
                    "txn_id": "T1",
                    "timestamp": "2026-01-01T10:00:00",
                    "type": "CREDIT",
                    "amount": "20000.00",
                    "utr": "UTR-V1",
                    "narration": "Disputed deposit",
                },
                {
                    "txn_id": "T2",
                    "timestamp": "2026-01-01T11:00:00",
                    "type": "DEBIT",
                    "amount": "15000.00",
                    "utr": "OUT-01",
                    "narration": "Withdrawal",
                },
            ],
        }

    def test_baseline_agreement_sop_ill1(self):
        """Verify DISPUTED_FIRST scenario perfectly matches SOP_ILL_1 attribution output."""
        res = analyze_sensitivity(self.case_ill1, self.attr_ill1)
        self.assertTrue(res["baseline_validated"])
        self.assertIsNone(res["validation_error"])

        disp = res["scenarios"]["DISPUTED_FIRST"]
        self.assertEqual(disp["scenario_remaining_clean"], "873.00")
        self.assertEqual(disp["total_scenario_attributed"], "158000.00")
        self.assertEqual(disp["scenario_remaining_attributed"]["B"], "8000.00")
        self.assertEqual(disp["scenario_remaining_attributed"]["A"], "0.00")
        self.assertEqual(disp["scenario_remaining_attributed"]["C"], "150000.00")

    def test_baseline_agreement_sop_ill2(self):
        """Verify DISPUTED_FIRST scenario matches SOP_ILL_2 attribution output."""
        res = analyze_sensitivity(self.case_ill2, self.attr_ill2)
        self.assertTrue(res["baseline_validated"])
        self.assertIsNone(res["validation_error"])

        disp = res["scenarios"]["DISPUTED_FIRST"]
        self.assertEqual(disp["scenario_remaining_clean"], "0.00")
        self.assertEqual(disp["total_scenario_attributed"], "206543.00")
        for v in self.attr_ill2["victims"]:
            cid = v["complaint_id"]
            self.assertEqual(disp["scenario_remaining_attributed"][cid], v["restorable_amount"])

    def test_baseline_agreement_merchant200(self):
        """Verify DISPUTED_FIRST scenario matches MERCHANT_200 attribution output."""
        res = analyze_sensitivity(self.case_m200, self.attr_m200)
        self.assertTrue(res["baseline_validated"])
        self.assertIsNone(res["validation_error"])

        disp = res["scenarios"]["DISPUTED_FIRST"]
        self.assertEqual(disp["scenario_remaining_clean"], "485000.00")
        self.assertEqual(disp["total_scenario_attributed"], "200.00")
        self.assertEqual(disp["scenario_remaining_attributed"]["P1"], "200.00")

    def test_three_scenarios_controlled_case(self):
        """Test that all three scenarios produce logically distinct and predictable outputs."""
        # Controlled case: Opening 10k clean, +20k disputed V1, -15k debit. Total balance remaining = 15k.
        res = analyze_sensitivity(self.controlled_case)
        scenarios = res["scenarios"]
        self.assertIn("DISPUTED_FIRST", scenarios)
        self.assertIn("CLEAN_FIRST", scenarios)
        self.assertIn("PROPORTIONAL", scenarios)

        disp = scenarios["DISPUTED_FIRST"]
        # Disputed first: Debit 15k comes entirely from V1 (20k). V1 has 5k left, clean has 10k left.
        self.assertEqual(disp["scenario_remaining_clean"], "10000.00")
        self.assertEqual(disp["scenario_remaining_attributed"]["V1"], "5000.00")
        self.assertEqual(disp["total_scenario_attributed"], "5000.00")

        clean = scenarios["CLEAN_FIRST"]
        # Clean first: Debit 15k consumes all 10k clean + 5k from V1. Clean has 0k left, V1 has 15k left.
        self.assertEqual(clean["scenario_remaining_clean"], "0.00")
        self.assertEqual(clean["scenario_remaining_attributed"]["V1"], "15000.00")
        self.assertEqual(clean["total_scenario_attributed"], "15000.00")

        prop = scenarios["PROPORTIONAL"]
        # Proportional: Available before debit = 10k clean + 20k disputed = 30k total (1/3 clean, 2/3 disputed).
        # Debit 15k: 1/3 (5k) from clean, 2/3 (10k) from disputed V1.
        # Clean remaining: 10k - 5k = 5000.00; V1 remaining: 20k - 10k = 10000.00.
        self.assertEqual(prop["scenario_remaining_clean"], "5000.00")
        self.assertEqual(prop["scenario_remaining_attributed"]["V1"], "10000.00")
        self.assertEqual(prop["total_scenario_attributed"], "10000.00")

    def test_conservation_and_reconciliation(self):
        """Assert that clean + total attributed == closing ledger balance across all scenarios."""
        test_cases = [self.case_ill1, self.case_ill2, self.case_m200, self.controlled_case]
        for c in test_cases:
            res = analyze_sensitivity(c)
            for sname, sdata in res["scenarios"].items():
                clean = Decimal(sdata["scenario_remaining_clean"])
                attr_total = Decimal(sdata["total_scenario_attributed"])
                ledger = Decimal(sdata["closing_ledger_balance"])
                recon_diff = Decimal(sdata["reconciliation_difference"])

                self.assertEqual(
                    clean + attr_total + recon_diff,
                    ledger,
                    f"Conservation violated in {c.get('case_id')} scenario {sname}"
                )
                self.assertEqual(recon_diff, Decimal("0.00"))

    def test_deterministic_results(self):
        """Assert two runs on identical input yield identical output."""
        res1 = analyze_sensitivity(self.case_ill1, self.attr_ill1)
        res2 = analyze_sensitivity(self.case_ill1, self.attr_ill1)
        self.assertEqual(json.dumps(res1, sort_keys=True), json.dumps(res2, sort_keys=True))

    def test_input_not_mutated(self):
        """Assert input dictionary is never mutated."""
        case_copy = copy.deepcopy(self.case_ill1)
        analyze_sensitivity(self.case_ill1, self.attr_ill1)
        self.assertEqual(self.case_ill1, case_copy)

    def test_missing_or_invalid_input(self):
        """Assert malformed or missing case input handles errors gracefully."""
        res_empty = analyze_sensitivity({})
        self.assertFalse(res_empty["baseline_validated"])
        self.assertIn("Invalid case input", res_empty["validation_error"])

        res_none = analyze_sensitivity(None)
        self.assertFalse(res_none["baseline_validated"])

    def test_labels_and_disclaimers(self):
        """Assert disclaimers explicitly label assumptions and avoid legal restoration claims."""
        res = analyze_sensitivity(self.case_ill1)
        self.assertIn("Hypothetical sensitivity analysis only", res["disclaimer"])
        self.assertIn("not an official sop policy", res["disclaimer"].lower())

        forbidden_phrases = ["legally recoverable", "legally due", "court order", "adjudicated"]
        for sname, sdata in res["scenarios"].items():
            self.assertIn("scenario_remaining_attributed", sdata)
            self.assertIn("scenario_remaining_clean", sdata)
            combined_text = (sdata["rule"] + " ".join(sdata["limitations"])).lower()
            for phrase in forbidden_phrases:
                self.assertNotIn(phrase, combined_text)


if __name__ == "__main__":
    unittest.main()
