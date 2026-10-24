"""
check_my_work.py  --  THE REFEREE.  OWNER: Integrator.  NOBODY ELSE MAY EDIT THIS FILE.

Usage (run inside the mercy_ledger folder):
    python check_my_work.py attribution
    python check_my_work.py simulator
    python check_my_work.py triage
    python check_my_work.py sla
    python check_my_work.py impact
    python check_my_work.py grievance
    python check_my_work.py orders
    python check_my_work.py all
It prints PASS or FAIL in plain English. Python standard library only.
"""
import sys, os, json, copy, re, importlib
from datetime import datetime, date
from decimal import Decimal
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
GOLD = os.path.join(HERE, "golden")
G = lambda name: json.load(open(os.path.join(GOLD, name), encoding="utf-8"))
FAILS = []

def fail(msg): FAILS.append(msg)

def diff(a, b, path="$", out=None):
    out = [] if out is None else out
    if len(out) >= 6: return out
    if type(a) != type(b):
        out.append("%s: expected %s %r but got %s %r" % (path, type(a).__name__, a, type(b).__name__, b)); return out
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in b: out.append("%s.%s: MISSING key in your output" % (path, k))
            elif k not in a: out.append("%s.%s: EXTRA key not in contract (remove it)" % (path, k))
            else: diff(a[k], b[k], "%s.%s" % (path, k), out)
    elif isinstance(a, list):
        if len(a) != len(b): out.append("%s: expected list of %d items, got %d" % (path, len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)): diff(x, y, "%s[%d]" % (path, i), out)
    elif ".epochs[" in path and path.endswith(".note"):
        if not (isinstance(b, str) and b.strip()): out.append("%s: must be a non-empty sentence (wording is free)" % path)
    elif a != b:
        out.append("%s: expected %r but got %r" % (path, a, b))
    return out

def has_float(o):
    if isinstance(o, float): return True
    if isinstance(o, dict): return any(has_float(v) for v in o.values())
    if isinstance(o, list): return any(has_float(v) for v in o)
    return False

def as_json(label, obj):
    try: return json.loads(json.dumps(obj))
    except TypeError as e:
        fail("%s: output is not plain JSON (%s). Money must be STRINGS like \"1500.00\", never Decimal/float objects." % (label, e)); return None

def compare(label, expected, got):
    j = as_json(label, got)
    if j is None: return
    if has_float(j): fail("%s: output contains a float number. Use strings for money." % label)
    for d in diff(expected, j): fail("%s -> %s" % (label, d))

def source_scan(mod, banned, no_float=True):
    src = open(os.path.join(HERE, mod + ".py"), encoding="utf-8").read()
    if "MERCY_LEDGER_STUB" in src:
        fail("%s.py is still the STUB file. Replace the whole file with your real code." % mod); return False
    body = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
    for b in banned + (["float("] if no_float else []):
        if b in body: fail("%s.py contains forbidden text %r (see rules)." % (mod, b))
    return True

BANNED = ["import requests", "urllib", "socket", "openai", "anthropic", "subprocess", "os.system", "eval(", "exec(",
          "datetime.now", "date.today", "time.time", "import random", "open(", "input("]

def load(mod):
    try: return importlib.import_module(mod)
    except Exception as e: fail("%s.py cannot be imported: %s: %s" % (mod, type(e).__name__, e)); return None

def run(label, fn, *a):
    try: return fn(*a)
    except Exception as e: fail("%s crashed: %s: %s" % (label, type(e).__name__, e)); return None

PRESET_IDS = ["SOP_ILL_1", "SOP_ILL_2", "MERCHANT_200"]
ALL_IDS = PRESET_IDS + ["EXTRA_MIXED", "EXTRA_ESCROW", "EXTRA_INVOICE_BAD", "EXTRA_INJECTION"]

def check_attribution():
    if not source_scan("attribution", BANNED): return
    m = load("attribution")
    if not m: return
    for cid in ["SOP_ILL_1", "SOP_ILL_2", "MERCHANT_200", "EXTRA_MIXED"]:
        case = G(cid + ".case.json"); before = copy.deepcopy(case)
        out = run("analyze_attribution(%s)" % cid, m.analyze_attribution, case)
        if out is None: continue
        compare("attribution[%s]" % cid, G(cid + ".attribution.json"), out)
        if case != before: fail("attribution[%s]: you modified the input case. Never change inputs." % cid)
        out2 = run("analyze_attribution(%s) 2nd call" % cid, m.analyze_attribution, copy.deepcopy(before))
        if out2 is not None and as_json("again", out2) != as_json("again", out): fail("attribution[%s]: two runs gave different answers." % cid)

def validate_case(c):
    errs = []
    need = ["case_id", "tier", "title", "description", "demo_today", "account", "opening_balance", "transactions", "complaints", "seizure_timestamp", "sla_context", "invoices"]
    for k in need:
        if k not in c: errs.append("missing key %s" % k)
    if errs: return errs
    money = re.compile(r"^\d+\.\d{2}$")
    for k in ["account_id", "account_type", "layer", "holder_name"]:
        if k not in c["account"]: errs.append("account missing %s" % k)
    if c["account"].get("account_type") not in ("SAVINGS", "CURRENT", "NODAL", "POOL", "ESCROW"): errs.append("bad account_type")
    for k in ["account_holder_complaint_on", "grievance_filed_on", "io_decision_on", "io_direction_on", "suspension_started_on"]:
        if k not in c["sla_context"]: errs.append("sla_context missing %s" % k)
    try: date.fromisoformat(c["demo_today"])
    except Exception: errs.append("bad demo_today")
    if not money.match(c["opening_balance"]): errs.append("opening_balance not money string")
    bal = Decimal(c["opening_balance"]); last = None; credits = {}
    for t in c["transactions"]:
        for k in ["txn_id", "timestamp", "type", "amount", "utr", "narration"]:
            if k not in t: errs.append("txn missing %s" % k); return errs
        if not money.match(t["amount"]): errs.append("txn amount not money string")
        ts = datetime.fromisoformat(t["timestamp"])
        if last and ts < last: errs.append("transactions not in time order")
        last = ts
        if t["type"] == "CREDIT": bal += Decimal(t["amount"]); credits[t["utr"]] = t
        elif t["type"] == "DEBIT": bal -= Decimal(t["amount"])
        else: errs.append("txn type must be CREDIT or DEBIT")
        if bal < 0: errs.append("balance went negative")
    ids = set()
    for p in c["complaints"]:
        for k in ["complaint_id", "victim_label", "state", "disputed_utr", "disputed_amount", "complaint_timestamp"]:
            if k not in p: errs.append("complaint missing %s" % k); return errs
        if p["complaint_id"] in ids: errs.append("duplicate complaint_id")
        ids.add(p["complaint_id"])
        t = credits.get(p["disputed_utr"])
        if not t: errs.append("complaint UTR has no matching credit")
        elif Decimal(p["disputed_amount"]) > Decimal(t["amount"]): errs.append("disputed more than credited")
        elif datetime.fromisoformat(p["complaint_timestamp"]) <= datetime.fromisoformat(t["timestamp"]): errs.append("complaint before credit")
    if len([t for t in c["transactions"] if t["utr"] in {p["disputed_utr"] for p in c["complaints"]}]) != len(c["complaints"]): errs.append("each disputed UTR must appear exactly once")
    return errs

def check_simulator():
    if not source_scan("simulator", [b for b in BANNED if b != "import random"], no_float=True): return
    m = load("simulator")
    if not m: return
    a = run("generate_cases(12, 7)", m.generate_cases, 12, 7)
    if a is None: return
    if not isinstance(a, list) or len(a) != 12: fail("generate_cases(12,7) must return a list of exactly 12 cases"); return
    b = run("generate_cases(12, 7) again", m.generate_cases, 12, 7)
    if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True): fail("same seed gave different cases (must be deterministic).")
    c = run("generate_cases(12, 8)", m.generate_cases, 12, 8)
    if c is not None and json.dumps(a, sort_keys=True) == json.dumps(c, sort_keys=True): fail("different seeds gave identical cases.")
    ids = [x.get("case_id") for x in a]
    if len(set(ids)) != len(ids): fail("case_id values must be unique")
    for x in a:
        for e in validate_case(x): fail("simulated case %s: %s" % (x.get("case_id"), e))
        if x.get("tier") != 3: fail("simulated case %s must have tier 3" % x.get("case_id"))
    big = run("generate_cases(40, 7)", m.generate_cases, 40, 7)
    if big is not None and len(big) != 40: fail("generate_cases(40,7) must return 40 cases")
    if big and not any(len(x["complaints"]) >= 3 for x in big): fail("simulation should include some cases with 3+ victims")
    if big and not any(len(x["complaints"]) == 1 and Decimal(x["opening_balance"]) >= 100000 for x in big): fail("simulation should include merchant-like cases: 1 complaint and opening_balance >= 100000.00")
    try:
        at = importlib.import_module("attribution")
        if "MERCY_LEDGER_STUB" not in open(os.path.join(HERE, "attribution.py")).read() and big:
            for x in big[:40]:
                try: at.analyze_attribution(x)
                except Exception as e: fail("real attribution crashed on simulated %s: %s" % (x["case_id"], e)); break
    except Exception: pass

def check_triage():
    if not source_scan("triage", BANNED): return
    m = load("triage")
    if not m: return
    for cid in ["SOP_ILL_1", "SOP_ILL_2", "MERCHANT_200", "EXTRA_MIXED", "EXTRA_ESCROW"]:
        case = G(cid + ".case.json"); before = copy.deepcopy(case)
        out = run("triage(%s)" % cid, m.triage, case, G(cid + ".attribution.json"), G(cid + ".grievance.json"))
        if out is not None: compare("triage[%s]" % cid, G(cid + ".triage.json"), out)
        if case != before: fail("triage[%s]: modified input" % cid)
    out = run("triage(grievance=None)", m.triage, G("SOP_ILL_1.case.json"), G("SOP_ILL_1.attribution.json"), None)
    if out is not None and out.get("recommendation") != "SEIZURE_S106": fail("triage with grievance=None must still work (treat as no documents).")

def check_sla():
    if not source_scan("sla", BANNED): return
    m = load("sla")
    if not m: return
    for cid in ALL_IDS:
        case = G(cid + ".case.json")
        out = run("compute_sla(%s)" % cid, m.compute_sla, case, case["demo_today"])
        if out is not None: compare("sla[%s]" % cid, G(cid + ".sla.json"), out)
    for d in ["2025-01-04", "2025-01-05"]:
        out = run("compute_sla(as_of=%s)" % d, m.compute_sla, G("SOP_ILL_1.case.json"), d)
        if out is not None: compare("sla[SOP_ILL_1 as_of %s]" % d, G("SOP_ILL_1.sla.asof_%s.json" % d), out)

def check_impact():
    if not source_scan("impact", BANNED): return
    m = load("impact")
    if not m: return
    items = []
    for cid in PRESET_IDS + ["EXTRA_MIXED", "EXTRA_ESCROW"]:
        out = run("case_impact(%s)" % cid, m.case_impact, G(cid + ".case.json"), G(cid + ".attribution.json"), G(cid + ".triage.json"))
        if out is not None: compare("impact[%s]" % cid, G(cid + ".impact.json"), out)
    items = [G(c + ".impact.json") for c in PRESET_IDS]
    out = run("aggregate_impact", m.aggregate_impact, items)
    if out is not None: compare("aggregate_impact[presets]", G("PRESETS.aggregate_impact.json"), out)
    z = run("aggregate_impact([]) must not crash", m.aggregate_impact, [])
    if z is not None and not isinstance(z, dict): fail("aggregate_impact([]) must return a dict")

def check_grievance():
    if not source_scan("grievance", BANNED): return
    m = load("grievance")
    if not m: return
    for cid in ALL_IDS:
        case = G(cid + ".case.json"); before = copy.deepcopy(case)
        out = run("verify_grievance(%s)" % cid, m.verify_grievance, case)
        if out is not None: compare("grievance[%s]" % cid, G(cid + ".grievance.json"), out)
        if case != before: fail("grievance[%s]: modified input" % cid)

def check_orders():
    if not source_scan("orders", BANNED): return
    m = load("orders")
    if not m: return
    exp = G("orders_expectations.json")
    for cid in ALL_IDS:
        args = [G(cid + ".case.json"), G(cid + ".attribution.json"), G(cid + ".triage.json"), G(cid + ".sla.json"), G(cid + ".grievance.json")]
        out = run("build_orders(%s)" % cid, m.build_orders, *args)
        if out is None: continue
        if not isinstance(out, dict) or set(out) != {"restoration_order_html", "indemnity_bond_html", "edd_packet_html"}:
            fail("orders[%s]: must return a dict with exactly the keys restoration_order_html, indemnity_bond_html, edd_packet_html" % cid); continue
        for k, v in out.items():
            if not isinstance(v, str) or "<html" not in v.lower(): fail("orders[%s].%s must be a full HTML string" % (cid, k)); continue
            if "DRAFT" not in v: fail("orders[%s].%s must visibly say DRAFT (officer sign-off required)" % (cid, k))
            if "<script" in v.lower(): fail("orders[%s].%s contains <script> - all inputs must be HTML-escaped" % (cid, k))
        allhtml = " ".join(v for v in out.values() if isinstance(v, str))
        for s in exp.get(cid, []):
            if s not in allhtml: fail("orders[%s]: expected to find %s in the documents (Indian format, e.g. \u20b91,50,000.00)" % (cid, s))
        r = out.get("restoration_order_html", "")
        if "106(3)" not in r or "BNSS" not in r: fail("orders[%s]: restoration order must mention Section 106(3) BNSS" % cid)
        if cid == "EXTRA_INJECTION" and "&lt;script&gt;" not in allhtml: fail("orders[EXTRA_INJECTION]: holder name must appear HTML-escaped (&lt;script&gt;)")
        if re.search(r"\d+\.\d+e", allhtml): fail("orders[%s]: looks like a float leaked into the text" % cid)

def check_pipeline():
    required = ["attribution", "simulator", "triage", "sla", "impact", "grievance", "orders"]
    remaining = []
    for mod in required:
        path = os.path.join(HERE, mod + ".py")
        try:
            if "MERCY_LEDGER_STUB" in open(path, encoding="utf-8").read():
                remaining.append(mod)
        except OSError:
            remaining.append(mod + " (missing)")
    if remaining:
        fail("pipeline: required modules are still stubs: " + ", ".join(remaining))
        return
    import pipeline, presets
    for cid in PRESET_IDS:
        r = pipeline.analyze(presets.PRESETS[cid])
        for e in r["errors"]: fail("pipeline[%s]: %s" % (cid, e))
        for key in ["attribution", "triage", "sla", "grievance", "impact", "orders"]:
            if r.get(key) is None: fail("pipeline[%s]: %s returned null" % (cid, key))
        if not isinstance(r.get("errors"), list): fail("pipeline[%s]: errors must be a list" % cid)
    p = pipeline.portfolio()
    for e in p["errors"]: fail("portfolio: %s" % e)
    if p.get("aggregate") is None: fail("portfolio: aggregate is null")

CHECKS = {"attribution": check_attribution, "simulator": check_simulator, "triage": check_triage, "sla": check_sla,
          "impact": check_impact, "grievance": check_grievance, "orders": check_orders}

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    names = list(CHECKS) if arg == "all" else ([arg] if arg in CHECKS else [])
    if not names:
        print("Usage: python check_my_work.py [%s|all]" % "|".join(CHECKS)); sys.exit(2)
    for n in names:
        start = len(FAILS); CHECKS[n]()
        print(("PASS  " if len(FAILS) == start else "FAIL  ") + n)
    if arg == "all":
        start = len(FAILS); check_pipeline(); print(("PASS  " if len(FAILS) == start else "FAIL  ") + "pipeline (whole system)")
    if FAILS:
        print("\nPROBLEMS (first 25) - copy these back to your AI and say 'fix exactly these, change nothing else':")
        for f in FAILS[:25]: print(" -", f)
        sys.exit(1)
    print("\nALL GOOD. Send your file(s) to the integrator.")

if __name__ == "__main__": main()
