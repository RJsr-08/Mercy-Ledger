"""Refresh the offline-demo cache only from real implemented modules."""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
REQUIRED = ["attribution", "simulator", "triage", "sla", "impact", "grievance", "orders"]
stubs = []
for name in REQUIRED:
    path = os.path.join(HERE, name + ".py")
    try:
        if "MERCY_LEDGER_STUB" in open(path, encoding="utf-8").read():
            stubs.append(name)
    except OSError:
        stubs.append(name + " (missing)")
if stubs:
    print("REFUSED: cannot refresh offline sample data from placeholder modules: " + ", ".join(stubs))
    sys.exit(2)

import presets
import pipeline

data = {"PRESETS": presets.list_presets(), "CASES": {}, "PORTFOLIO": pipeline.portfolio()}
if data["PORTFOLIO"].get("errors"):
    print("REFUSED: portfolio generation returned errors: " + "; ".join(data["PORTFOLIO"]["errors"]))
    sys.exit(2)
for key, case in presets.PRESETS.items():
    result = pipeline.analyze(case)
    if result.get("errors"):
        print("REFUSED: case %s failed: %s" % (key, "; ".join(result["errors"])))
        sys.exit(2)
    data["CASES"][key] = result
out_path = os.path.join(HERE, "static", "sample_data.js")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("window.SAMPLE = " + json.dumps(data, ensure_ascii=False) + ";\n")
print("wrote static/sample_data.js from implemented modules")
