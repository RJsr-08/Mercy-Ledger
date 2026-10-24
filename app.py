"""
app.py -- the web server. OWNER: Integrator.
Run:  python -m uvicorn app:app --reload      then open http://127.0.0.1:8000
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Any, Dict
import presets, pipeline

# Optional Priority 2 and Priority 3 helpers
try:
    import review_flags
except ImportError:
    review_flags = None

try:
    import invariants
except ImportError:
    invariants = None

try:
    import stress_test
except ImportError:
    stress_test = None

try:
    import victim_explainer
except ImportError:
    victim_explainer = None

try:
    import sensitivity
except ImportError:
    sensitivity = None

try:
    import chain
except ImportError:
    chain = None

try:
    import audit_integrity
except ImportError:
    audit_integrity = None


app = FastAPI(title="Mercy Ledger", version="2.0")
HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "static")


class AnalyzeRequest(BaseModel):
    preset_id: Optional[str] = None
    case: Optional[Dict[str, Any]] = None
    as_of: Optional[str] = None   # "YYYY-MM-DD"


class FingerprintRequest(BaseModel):
    preset_id: Optional[str] = None
    case: Optional[Dict[str, Any]] = None
    expected_digest: Optional[str] = None


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/presets")
def api_presets():
    return presets.list_presets()


@app.get("/api/presets/{preset_id}")
def api_preset(preset_id: str):
    if preset_id not in presets.PRESETS:
        raise HTTPException(404, "unknown preset")
    return presets.get_preset(preset_id)


@app.post("/api/analyze-case")
def api_analyze(req: AnalyzeRequest):
    if req.preset_id:
        if req.preset_id not in presets.PRESETS:
            raise HTTPException(404, "unknown preset")
        case = presets.get_preset(req.preset_id)
    elif req.case:
        case = req.case
    else:
        raise HTTPException(400, "send preset_id or case")
    return pipeline.analyze(case, req.as_of)


@app.get("/api/portfolio-impact")
def api_portfolio(n_sim: int = 40, seed: int = 7):
    return pipeline.portfolio(min(max(n_sim, 0), 200), seed)


# ── Priority 2 Endpoints ──────────────────────────────────────────────────────

def _get_analysis_extras_for_case(case):
    analysis = pipeline.analyze(case)
    attr = analysis.get("attribution")
    grv = analysis.get("grievance")

    rf = None
    if review_flags and attr:
        try:
            rf = review_flags.build_review_flags(case, attr, grv)
        except Exception as e:
            rf = {"error": f"Review flags failed: {e}"}

    inv = None
    if invariants and attr:
        try:
            inv = invariants.check_case_invariants(case, attr)
        except Exception as e:
            inv = {"error": f"Invariants failed: {e}"}

    vexp = None
    if victim_explainer and attr:
        try:
            vexp = victim_explainer.explain_victims(case, attr)
        except Exception as e:
            vexp = {"error": f"Victim explainer failed: {e}"}

    return {
        "case_id": case.get("case_id", "UNKNOWN"),
        "review_flags": rf,
        "invariants": inv,
        "victim_explanations": vexp,
    }


@app.get("/api/analysis-extras/{preset_id}")
def api_analysis_extras(preset_id: str):
    if preset_id not in presets.PRESETS:
        raise HTTPException(404, "unknown preset")
    case = presets.get_preset(preset_id)
    return _get_analysis_extras_for_case(case)


@app.post("/api/analysis-extras")
def api_analysis_extras_post(req: AnalyzeRequest):
    if req.preset_id:
        if req.preset_id not in presets.PRESETS:
            raise HTTPException(404, "unknown preset")
        case = presets.get_preset(req.preset_id)
    elif req.case:
        case = req.case
    else:
        raise HTTPException(400, "send preset_id or case")
    return _get_analysis_extras_for_case(case)


@app.get("/api/stress-test")
def api_stress_test(n: int = 40, seed: int = 7):
    if not stress_test:
        raise HTTPException(501, "stress_test module not available")
    return stress_test.run_stress_test(min(max(n, 1), 200), seed)


# ── Priority 3 Endpoints ──────────────────────────────────────────────────────

@app.get("/api/sensitivity/{preset_id}")
def api_sensitivity(preset_id: str):
    if preset_id not in presets.PRESETS:
        raise HTTPException(404, "unknown preset")
    if not sensitivity:
        raise HTTPException(501, "sensitivity module not available")
    case = presets.get_preset(preset_id)
    return sensitivity.analyze_sensitivity(case)


@app.post("/api/sensitivity")
def api_sensitivity_post(req: AnalyzeRequest):
    if not sensitivity:
        raise HTTPException(501, "sensitivity module not available")
    if req.preset_id:
        if req.preset_id not in presets.PRESETS:
            raise HTTPException(404, "unknown preset")
        case = presets.get_preset(req.preset_id)
    elif req.case:
        case = req.case
    else:
        raise HTTPException(400, "send preset_id or case")
    return sensitivity.analyze_sensitivity(case)


@app.get("/api/chain-demo")
def api_chain_demo():
    if not chain:
        raise HTTPException(501, "chain module not available")
    demo_dataset = chain.create_synthetic_chain_demo()
    return chain.trace_chains(demo_dataset)


@app.post("/api/audit-fingerprint")
def api_fingerprint(req: FingerprintRequest):
    if not audit_integrity:
        raise HTTPException(501, "audit_integrity module not available")
    if req.preset_id:
        if req.preset_id not in presets.PRESETS:
            raise HTTPException(404, "unknown preset")
        case = presets.get_preset(req.preset_id)
    elif req.case:
        case = req.case
    else:
        raise HTTPException(400, "send preset_id or case")

    analysis = pipeline.analyze(case)
    engine_ver = "2.0.0"

    if req.expected_digest:
        return audit_integrity.verify_fingerprint(case, engine_ver, analysis, req.expected_digest)
    return audit_integrity.create_fingerprint(case, engine_ver, analysis)


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC, "index.html"))


app.mount("/static", StaticFiles(directory=STATIC), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

