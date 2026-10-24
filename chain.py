"""Controlled multi-account transfer link graph for Mercy Ledger.

Models multi-layer mule account tracing (BPR&D Compendium: Challenges in Tracing
Money Trail in Cyber Fraud; RBI Fraud Risk Management Directions 2024)
to explore multi-account transaction flows and downstream links,
categorizing edges into VERIFIED_LINK, CANDIDATE_LINK, UNRESOLVED, and AMBIGUOUS_CANDIDATE.

This is a synthetic demonstration and analytical exploration tool. It does not
assert exact per-rupee ownership, live bank tracing, or legal liability.
"""
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def _money(val):
    if not isinstance(val, Decimal):
        val = Decimal(str(val))
    return format(val.quantize(CENT, rounding=ROUND_HALF_UP), ".2f")


def trace_chains(dataset):
    """Trace transaction links across multi-account records in a dataset.

    Args:
        dataset: dict containing:
            - "accounts": list of dicts with account_id, holder_name, layer, etc.
            - "transactions": list of dicts with txn_id, account_id, timestamp,
                              direction ("DEBIT"|"CREDIT"), amount, utr,
                              transfer_id (optional), counterparty_account (optional).

    Returns:
        dict with nodes, edges, paths, warnings, and summary.
    """
    if not isinstance(dataset, dict):
        return {
            "nodes": [],
            "edges": [],
            "paths": [],
            "warnings": ["Invalid dataset format: expected dictionary"],
            "summary": "Chain tracing failed: invalid input format.",
        }

    accounts = dataset.get("accounts", [])
    raw_txns = dataset.get("transactions", [])
    warnings = []

    # Map accounts
    nodes_dict = {}
    for acc in accounts:
        aid = acc.get("account_id")
        if aid:
            nodes_dict[aid] = {
                "id": aid,
                "account_id": aid,
                "holder_name": acc.get("holder_name", f"Account {aid}"),
                "layer": acc.get("layer", 1),
                "account_type": acc.get("account_type", "SAVINGS"),
            }

    # Separate debits and credits
    debits = []
    credits_by_transfer_id = {}
    credits_by_utr_amt = {}

    for t in sorted(raw_txns, key=lambda x: x.get("timestamp", "")):
        aid = t.get("account_id")
        if aid and aid not in nodes_dict:
            nodes_dict[aid] = {
                "id": aid,
                "account_id": aid,
                "holder_name": f"Account {aid}",
                "layer": 1,
                "account_type": "UNKNOWN",
            }

        direction = t.get("direction", "").upper()
        if direction == "DEBIT":
            debits.append(t)
        elif direction == "CREDIT":
            tid = t.get("transfer_id")
            if tid:
                credits_by_transfer_id.setdefault(tid, []).append(t)
            utr = t.get("utr")
            amt_str = _money(Decimal(str(t.get("amount", "0.00"))))
            if utr:
                credits_by_utr_amt.setdefault((utr, amt_str), []).append(t)

    edges = []
    edge_id_counter = 1
    used_credit_txns = set()

    for d in debits:
        d_txn_id = d.get("txn_id")
        src_account = d.get("account_id")
        d_amt = Decimal(str(d.get("amount", "0.00")))
        d_amt_str = _money(d_amt)
        d_ts = d.get("timestamp", "")
        d_transfer_id = d.get("transfer_id")
        d_utr = d.get("utr")
        counterparty = d.get("counterparty_account")

        # 1. Check for explicit verified link via transfer_id
        matched = False
        if d_transfer_id and d_transfer_id in credits_by_transfer_id:
            candidate_credits = [
                c for c in credits_by_transfer_id[d_transfer_id]
                if c["txn_id"] not in used_credit_txns and c.get("timestamp", "") >= d_ts
            ]
            if len(candidate_credits) == 1:
                c = candidate_credits[0]
                target_account = c.get("account_id")
                edges.append({
                    "id": f"E{edge_id_counter}",
                    "source": src_account,
                    "target": target_account,
                    "amount": d_amt_str,
                    "match_status": "VERIFIED_LINK",
                    "evidence": f"Explicit transfer_id match: {d_transfer_id}",
                    "debit_txn_id": d_txn_id,
                    "credit_txn_id": c.get("txn_id"),
                    "timestamp": d_ts,
                })
                used_credit_txns.add(c["txn_id"])
                edge_id_counter += 1
                matched = True
            elif len(candidate_credits) > 1:
                # Ambiguous multiple matches with same transfer_id
                edges.append({
                    "id": f"E{edge_id_counter}",
                    "source": src_account,
                    "target": None,
                    "amount": d_amt_str,
                    "match_status": "AMBIGUOUS_CANDIDATE",
                    "evidence": f"Multiple ({len(candidate_credits)}) recipient credits share transfer_id {d_transfer_id}",
                    "debit_txn_id": d_txn_id,
                    "credit_txn_id": None,
                    "timestamp": d_ts,
                })
                edge_id_counter += 1
                matched = True
                warnings.append(f"Debit {d_txn_id} has ambiguous transfer_id matches.")

        if matched:
            continue

        # 2. Check for UTR and amount candidate match
        if d_utr:
            candidate_credits = [
                c for c in credits_by_utr_amt.get((d_utr, d_amt_str), [])
                if c["txn_id"] not in used_credit_txns and c.get("timestamp", "") >= d_ts
                and c.get("account_id") != src_account
            ]
            if len(candidate_credits) == 1:
                c = candidate_credits[0]
                target_account = c.get("account_id")
                edges.append({
                    "id": f"E{edge_id_counter}",
                    "source": src_account,
                    "target": target_account,
                    "amount": d_amt_str,
                    "match_status": "CANDIDATE_LINK",
                    "evidence": f"Matching UTR ({d_utr}) and amount ({d_amt_str}); unconfirmed reciprocal ID",
                    "debit_txn_id": d_txn_id,
                    "credit_txn_id": c.get("txn_id"),
                    "timestamp": d_ts,
                })
                used_credit_txns.add(c["txn_id"])
                edge_id_counter += 1
                matched = True
            elif len(candidate_credits) > 1:
                edges.append({
                    "id": f"E{edge_id_counter}",
                    "source": src_account,
                    "target": None,
                    "amount": d_amt_str,
                    "match_status": "AMBIGUOUS_CANDIDATE",
                    "evidence": f"Multiple ({len(candidate_credits)}) recipient credits share UTR {d_utr} and amount {d_amt_str}",
                    "debit_txn_id": d_txn_id,
                    "credit_txn_id": None,
                    "timestamp": d_ts,
                })
                edge_id_counter += 1
                matched = True
                warnings.append(f"Debit {d_txn_id} has ambiguous candidate matches.")

        if matched:
            continue

        # 3. If counterparty account is known but no credit in dataset, or completely missing
        edges.append({
            "id": f"E{edge_id_counter}",
            "source": src_account,
            "target": counterparty,
            "amount": d_amt_str,
            "match_status": "UNRESOLVED",
            "evidence": f"Outgoing transfer without matching credit in dataset (counterparty: {counterparty or 'unknown'})",
            "debit_txn_id": d_txn_id,
            "credit_txn_id": None,
            "timestamp": d_ts,
        })
        edge_id_counter += 1

    # Reconstruct paths (chains)
    adjacency = {}
    for edge in edges:
        if edge["match_status"] in ("VERIFIED_LINK", "CANDIDATE_LINK") and edge["target"]:
            adjacency.setdefault(edge["source"], []).append(edge)

    paths = []
    visited_edges = set()

    def build_paths_from(current_acc, current_path, seen_nodes):
        extended = False
        for edge in adjacency.get(current_acc, []):
            eid = edge["id"]
            target = edge["target"]
            if eid not in visited_edges and target not in seen_nodes:
                visited_edges.add(eid)
                build_paths_from(target, current_path + [edge], seen_nodes | {target})
                extended = True
        if not extended and len(current_path) >= 1:
            paths.append([
                {
                    "edge_id": e["id"],
                    "from_account": e["source"],
                    "to_account": e["target"],
                    "amount": e["amount"],
                    "match_status": e["match_status"],
                }
                for e in current_path
            ])

    for acc_id in nodes_dict:
        build_paths_from(acc_id, [], {acc_id})

    nodes = list(nodes_dict.values())
    summary = (
        f"Synthetic chain tracing analyzed {len(nodes)} accounts and {len(raw_txns)} transactions: "
        f"{len(edges)} edge(s) identified ({sum(1 for e in edges if e['match_status'] == 'VERIFIED_LINK')} verified, "
        f"{sum(1 for e in edges if e['match_status'] == 'CANDIDATE_LINK')} candidate, "
        f"{sum(1 for e in edges if e['match_status'] == 'UNRESOLVED')} unresolved)."
    )

    return {
        "nodes": nodes,
        "edges": edges,
        "paths": paths,
        "warnings": warnings,
        "summary": summary,
    }


def create_synthetic_chain_demo():
    """Create a deterministic multi-account synthetic dataset for demonstration and testing."""
    return {
        "accounts": [
            {"account_id": "ACC-L1", "holder_name": "Primary Mule Account", "layer": 1, "account_type": "SAVINGS"},
            {"account_id": "ACC-L2A", "holder_name": "Secondary Layer Account A", "layer": 2, "account_type": "CURRENT"},
            {"account_id": "ACC-L2B", "holder_name": "Secondary Layer Account B", "layer": 2, "account_type": "SAVINGS"},
            {"account_id": "ACC-L3", "holder_name": "Cash-Out Merchant Gateway", "layer": 3, "account_type": "ESCROW"},
        ],
        "transactions": [
            {
                "txn_id": "T-L1-01",
                "account_id": "ACC-L1",
                "timestamp": "2026-10-24T10:00:00",
                "direction": "DEBIT",
                "amount": "50000.00",
                "transfer_id": "TRF-001",
                "utr": "UTR-CHAIN-001",
                "counterparty_account": "ACC-L2A",
            },
            {
                "txn_id": "T-L2A-01",
                "account_id": "ACC-L2A",
                "timestamp": "2026-10-24T10:01:00",
                "direction": "CREDIT",
                "amount": "50000.00",
                "transfer_id": "TRF-001",
                "utr": "UTR-CHAIN-001",
            },
            {
                "txn_id": "T-L2A-02",
                "account_id": "ACC-L2A",
                "timestamp": "2026-10-24T10:15:00",
                "direction": "DEBIT",
                "amount": "20000.00",
                "utr": "UTR-CHAIN-002",
                "counterparty_account": "ACC-L3",
            },
            {
                "txn_id": "T-L3-01",
                "account_id": "ACC-L3",
                "timestamp": "2026-10-24T10:16:00",
                "direction": "CREDIT",
                "amount": "20000.00",
                "utr": "UTR-CHAIN-002",
            },
            {
                "txn_id": "T-L1-02",
                "account_id": "ACC-L1",
                "timestamp": "2026-10-24T10:30:00",
                "direction": "DEBIT",
                "amount": "15000.00",
                "utr": "UTR-UNRESOLVED",
                "counterparty_account": "ACC-EXTERNAL",
            },
        ],
    }
