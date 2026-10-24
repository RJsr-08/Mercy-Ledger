"""Unit tests for Priority 2 review flags module."""
import json
import os
import unittest
import copy
from decimal import Decimal

from review_flags import build_review_flags

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(HERE, "golden")


def _load_golden(name):
    path = os.path.join(GOLDEN, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestReviewFlags(unittest.TestCase):
    def setUp(self):
        self.case_ill1 = _load_golden("SOP_ILL_1.case.json")
        self.attr_ill1 = _load_golden("SOP_ILL_1.attribution.json")
        self.grv_ill1 = _load_golden("SOP_ILL_1.grievance.json")

        self.case_ill2 = _load_golden("SOP_ILL_2.case.json")
        self.attr_ill2 = _load_golden("SOP_ILL_2.attribution.json")
        self.grv_ill2 = _load_golden("SOP_ILL_2.grievance.json")

        self.case_m200 = _load_golden("MERCHANT_200.case.json")
        self.attr_m200 = _load_golden("MERCHANT_200.attribution.json")
        self.grv_m200 = _load_golden("MERCHANT_200.grievance.json")

    def test_hold_attribution_gap_triggered(self):
        """Cover a hold/attribution gap and verify both numbers are reported."""
        result = build_review_flags(self.case_ill1, self.attr_ill1, grievance=None)
        codes = [f["code"] for f in result["flags"]]
        self.assertIn("HOLD_ATTRIBUTION_GAP", codes)

        gap_flag = next(f for f in result["flags"] if f["code"] == "HOLD_ATTRIBUTION_GAP")
        self.assertEqual(gap_flag["severity"], "HIGH")
        # Check that both figures appear in the explanation
        self.assertIn("158873.00", gap_flag["explanation"])
        self.assertIn("158000.00", gap_flag["explanation"])
        # Discrepancy must not be labelled unlawful
        self.assertNotIn("unlawful", gap_flag["explanation"].lower())
        self.assertNotIn("illegal", gap_flag["explanation"].lower())

    def test_case_with_no_gap(self):
        """Cover cases with no hold/attribution gap."""
        # SOP_ILL_2 has equal hold totals (206543.00)
        res_ill2 = build_review_flags(self.case_ill2, self.attr_ill2, grievance=None)
        codes_ill2 = [f["code"] for f in res_ill2["flags"]]
        self.assertNotIn("HOLD_ATTRIBUTION_GAP", codes_ill2)

        # MERCHANT_200 has equal hold totals (200.00)
        res_m200 = build_review_flags(self.case_m200, self.attr_m200, grievance=self.grv_m200)
        codes_m200 = [f["code"] for f in res_m200["flags"]]
        self.assertNotIn("HOLD_ATTRIBUTION_GAP", codes_m200)
        self.assertEqual(res_m200["count"], 0)
        self.assertEqual(len(res_m200["flags"]), 0)

    def test_outflow_destination_unverified(self):
        """Cover outgoing transactions without verified destination linkage."""
        result = build_review_flags(self.case_ill1, self.attr_ill1, grievance=None)
        codes = [f["code"] for f in result["flags"]]
        self.assertIn("OUTFLOW_DESTINATION_UNVERIFIED", codes)

        outflow_flag = next(f for f in result["flags"] if f["code"] == "OUTFLOW_DESTINATION_UNVERIFIED")
        self.assertEqual(outflow_flag["severity"], "MEDIUM")
        # In SOP_ILL_1, T2 and T4 are debits that forwarded disputed funds
        self.assertIn("T2", outflow_flag["txn_ids"])
        self.assertIn("T4", outflow_flag["txn_ids"])
        self.assertIn("B", outflow_flag["complaint_ids"])
        self.assertIn("A", outflow_flag["complaint_ids"])
        # Explanation must clarify that destination is not established
        self.assertIn("destination is not established", outflow_flag["explanation"])

    def test_multiple_claims_review(self):
        """Cover multi-claim cases and single-claim cases."""
        # SOP_ILL_1 has 3 complaints
        res_multi = build_review_flags(self.case_ill1, self.attr_ill1, grievance=None)
        codes_multi = [f["code"] for f in res_multi["flags"]]
        self.assertIn("MULTIPLE_CLAIMS_REVIEW", codes_multi)
        multi_flag = next(f for f in res_multi["flags"] if f["code"] == "MULTIPLE_CLAIMS_REVIEW")
        self.assertEqual(len(multi_flag["complaint_ids"]), 3)
        self.assertIn("does not assert that claims overlap or conflict", multi_flag["explanation"])

        # MERCHANT_200 has 1 complaint -> must NOT trigger MULTIPLE_CLAIMS_REVIEW
        res_single = build_review_flags(self.case_m200, self.attr_m200, grievance=None)
        codes_single = [f["code"] for f in res_single["flags"]]
        self.assertNotIn("MULTIPLE_CLAIMS_REVIEW", codes_single)

    def test_evidence_not_complete(self):
        """Cover grievance verification evidence flag."""
        # SOP_ILL_1 grievance has no invoices submitted -> EVIDENCE_NOT_COMPLETE
        res_incomplete = build_review_flags(self.case_ill1, self.attr_ill1, grievance=self.grv_ill1)
        codes_incomplete = [f["code"] for f in res_incomplete["flags"]]
        self.assertIn("EVIDENCE_NOT_COMPLETE", codes_incomplete)
        flag = next(f for f in res_incomplete["flags"] if f["code"] == "EVIDENCE_NOT_COMPLETE")
        self.assertEqual(flag["severity"], "HIGH")
        self.assertIn("NO_INVOICE", flag["explanation"])

        # Grievance is None -> must NOT trigger EVIDENCE_NOT_COMPLETE
        res_no_grv = build_review_flags(self.case_ill1, self.attr_ill1, grievance=None)
        self.assertNotIn("EVIDENCE_NOT_COMPLETE", [f["code"] for f in res_no_grv["flags"]])

        # MERCHANT_200 grievance is fully matched -> must NOT trigger EVIDENCE_NOT_COMPLETE
        res_matched = build_review_flags(self.case_m200, self.attr_m200, grievance=self.grv_m200)
        self.assertNotIn("EVIDENCE_NOT_COMPLETE", [f["code"] for f in res_matched["flags"]])

    def test_objective_wording_no_criminal_or_unlawful_claims(self):
        """Assert wording does not call a hold unlawful or an account holder criminal/guilty."""
        cases = [
            (self.case_ill1, self.attr_ill1, self.grv_ill1),
            (self.case_ill2, self.attr_ill2, self.grv_ill2),
            (self.case_m200, self.attr_m200, self.grv_m200),
        ]
        banned_terms = ["unlawful", "illegal", "criminal", "guilty", "fraudster", "culpable"]

        for case, attr, grv in cases:
            res = build_review_flags(case, attr, grv)
            all_text = [res["summary"]]
            for flag in res["flags"]:
                all_text.append(flag["title"])
                all_text.append(flag["explanation"])

            combined = " ".join(all_text).lower()
            for term in banned_terms:
                self.assertNotIn(
                    term, combined,
                    f"Forbidden prejudicial word '{term}' found in review flags for {case.get('case_id')}"
                )

    def test_pure_function_does_not_mutate_inputs(self):
        """Verify inputs are completely unmodified."""
        case_copy = copy.deepcopy(self.case_ill1)
        attr_copy = copy.deepcopy(self.attr_ill1)
        grv_copy = copy.deepcopy(self.grv_ill1)

        build_review_flags(self.case_ill1, self.attr_ill1, self.grv_ill1)

        self.assertEqual(self.case_ill1, case_copy)
        self.assertEqual(self.attr_ill1, attr_copy)
        self.assertEqual(self.grv_ill1, grv_copy)

    def test_json_safe_output(self):
        """Verify output serializes cleanly to JSON."""
        res = build_review_flags(self.case_ill1, self.attr_ill1, self.grv_ill1)
        dumped = json.dumps(res)
        self.assertIsInstance(dumped, str)
        loaded = json.loads(dumped)
        self.assertEqual(loaded["case_id"], "SOP_ILL_1")
        self.assertEqual(loaded["count"], len(loaded["flags"]))


if __name__ == "__main__":
    unittest.main()
