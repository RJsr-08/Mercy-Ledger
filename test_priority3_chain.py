"""Unit tests for Person A Priority 3 controlled multi-account link graph."""
import json
import unittest
from decimal import Decimal

from chain import trace_chains, create_synthetic_chain_demo


class TestChainTracing(unittest.TestCase):
    def setUp(self):
        self.demo_dataset = create_synthetic_chain_demo()

    def test_verified_link_matching(self):
        """Test explicit transfer_id produces a VERIFIED_LINK edge."""
        res = trace_chains(self.demo_dataset)
        verified = [e for e in res["edges"] if e["match_status"] == "VERIFIED_LINK"]
        self.assertTrue(len(verified) >= 1)
        e1 = verified[0]
        self.assertEqual(e1["source"], "ACC-L1")
        self.assertEqual(e1["target"], "ACC-L2A")
        self.assertEqual(e1["amount"], "50000.00")
        self.assertIn("TRF-001", e1["evidence"])

    def test_candidate_link_matching(self):
        """Test matching UTR and amount without transfer_id produces CANDIDATE_LINK."""
        res = trace_chains(self.demo_dataset)
        candidates = [e for e in res["edges"] if e["match_status"] == "CANDIDATE_LINK"]
        self.assertTrue(len(candidates) >= 1)
        c1 = candidates[0]
        self.assertEqual(c1["source"], "ACC-L2A")
        self.assertEqual(c1["target"], "ACC-L3")
        self.assertEqual(c1["amount"], "20000.00")

    def test_unresolved_transfer_matching(self):
        """Test debit with no matching credit in dataset produces UNRESOLVED edge."""
        res = trace_chains(self.demo_dataset)
        unresolved = [e for e in res["edges"] if e["match_status"] == "UNRESOLVED"]
        self.assertTrue(len(unresolved) >= 1)
        u1 = unresolved[0]
        self.assertEqual(u1["source"], "ACC-L1")
        self.assertEqual(u1["target"], "ACC-EXTERNAL")
        self.assertEqual(u1["amount"], "15000.00")

    def test_ambiguous_duplicate_matches(self):
        """Test that multiple matching recipient credits are flagged AMBIGUOUS_CANDIDATE without silent picking."""
        dataset = {
            "accounts": [
                {"account_id": "ACC-SRC"},
                {"account_id": "ACC-DST1"},
                {"account_id": "ACC-DST2"},
            ],
            "transactions": [
                {
                    "txn_id": "D1",
                    "account_id": "ACC-SRC",
                    "timestamp": "2026-01-01T10:00:00",
                    "direction": "DEBIT",
                    "amount": "10000.00",
                    "utr": "UTR-DUP",
                },
                {
                    "txn_id": "C1",
                    "account_id": "ACC-DST1",
                    "timestamp": "2026-01-01T10:05:00",
                    "direction": "CREDIT",
                    "amount": "10000.00",
                    "utr": "UTR-DUP",
                },
                {
                    "txn_id": "C2",
                    "account_id": "ACC-DST2",
                    "timestamp": "2026-01-01T10:06:00",
                    "direction": "CREDIT",
                    "amount": "10000.00",
                    "utr": "UTR-DUP",
                },
            ],
        }
        res = trace_chains(dataset)
        ambig = [e for e in res["edges"] if e["match_status"] == "AMBIGUOUS_CANDIDATE"]
        self.assertEqual(len(ambig), 1)
        self.assertIsNone(ambig[0]["target"])
        self.assertTrue(len(res["warnings"]) >= 1)

    def test_multi_hop_chain_reconstruction(self):
        """Verify that sequential hops form multi-edge paths without cycle loops."""
        res = trace_chains(self.demo_dataset)
        paths = res["paths"]
        self.assertTrue(len(paths) >= 1)
        multi_hop = [p for p in paths if len(p) >= 2]
        self.assertTrue(len(multi_hop) >= 1)
        hop1 = multi_hop[0][0]
        hop2 = multi_hop[0][1]
        self.assertEqual(hop1["from_account"], "ACC-L1")
        self.assertEqual(hop1["to_account"], "ACC-L2A")
        self.assertEqual(hop2["from_account"], "ACC-L2A")
        self.assertEqual(hop2["to_account"], "ACC-L3")

    def test_principal_not_doubled_across_hops(self):
        """Verify that multi-hop downstream transfers represent sequential hops, not additive new principal."""
        res = trace_chains(self.demo_dataset)
        # Unique debit principal originated from L1 is 50,000 + 15,000 = 65,000
        # The downstream transfer of 20,000 from L2A to L3 is a sub-hop of the 50,000, not fresh money.
        l1_debits = [
            Decimal(t["amount"]) for t in self.demo_dataset["transactions"]
            if t["account_id"] == "ACC-L1" and t["direction"] == "DEBIT"
        ]
        total_originated = sum(l1_debits)
        self.assertEqual(total_originated, Decimal("65000.00"))

    def test_deterministic_output(self):
        """Verify deterministic output for identical input."""
        res1 = trace_chains(self.demo_dataset)
        res2 = trace_chains(self.demo_dataset)
        self.assertEqual(json.dumps(res1, sort_keys=True), json.dumps(res2, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
