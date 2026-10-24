"""
pipeline.py -- glue. OWNER: Integrator. NOBODY ELSE MAY EDIT THIS FILE.
Plain Python (no web framework). app.py wraps this.
"""
import copy
from datetime import date
import presets, attribution, triage, sla, impact, grievance, orders, simulator

def _safe(name, fn, *args):
    try:
        return fn(*args), None
    except Exception as e:  # shown to the human instead of crashing
        return None, "%s failed: %s: %s" % (name, type(e).__name__, e)

def resolve_as_of(case, as_of=None):
    value = as_of or case.get("demo_today")
    if not value:
        raise ValueError("Provide as_of or case['demo_today']; the pipeline has no system-date fallback.")
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError("as_of must be a valid YYYY-MM-DD date string.")
    return value

def analyze(case, as_of=None):
    case = copy.deepcopy(case)
    as_of = resolve_as_of(case, as_of)
    errors = []
    attr, e = _safe("attribution", attribution.analyze_attribution, case); errors += [e] if e else []
    grv, e = _safe("grievance", grievance.verify_grievance, case); errors += [e] if e else []
    tri = imp = ords = None
    if attr is not None:
        tri, e = _safe("triage", triage.triage, case, attr, grv); errors += [e] if e else []
    slac, e = _safe("sla", sla.compute_sla, case, as_of); errors += [e] if e else []
    if attr is not None and tri is not None:
        imp, e = _safe("impact", impact.case_impact, case, attr, tri); errors += [e] if e else []
        if slac is not None and grv is not None:
            ords, e = _safe("orders", orders.build_orders, case, attr, tri, slac, grv); errors += [e] if e else []
    return {"case_id": case["case_id"], "title": case["title"], "tier": case.get("tier"),
            "description": case.get("description"), "as_of": as_of,
            "account": case["account"], "opening_balance": case["opening_balance"],
            "transactions": case["transactions"], "complaints": case["complaints"],
            "attribution": attr, "triage": tri, "sla": slac, "grievance": grv,
            "impact": imp, "orders": ords, "errors": errors}

def portfolio(n_sim=40, seed=7):
    cases = [copy.deepcopy(c) for c in presets.PRESETS.values()]
    sim, e = _safe("simulator", simulator.generate_cases, n_sim, seed)
    errors = [e] if e else []
    if sim: cases += sim
    items = []
    for c in cases:
        a, e1 = _safe("attribution", attribution.analyze_attribution, c)
        if a is None: errors.append(e1); continue
        g, _ = _safe("grievance", grievance.verify_grievance, c)
        t, e2 = _safe("triage", triage.triage, c, a, g)
        if t is None: errors.append(e2); continue
        i, e3 = _safe("impact", impact.case_impact, c, a, t)
        if i is None: errors.append(e3); continue
        items.append(i)
    agg, e = _safe("impact", impact.aggregate_impact, items) if items else (None, "no cases analysed")
    if e: errors.append(e)
    return {"aggregate": agg, "errors": sorted(set(x for x in errors if x))}
