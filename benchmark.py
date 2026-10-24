"""Benchmark the completed case-analysis pipeline; refuses to time stub outputs."""
import os
import sys
import time

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
    print("NOT RUN: replace these placeholder modules first: " + ", ".join(stubs))
    print("Do not quote the stub pipeline's speed as application performance.")
    sys.exit(2)

import presets
import pipeline

cases = list(presets.PRESETS.values())
if not cases:
    print("NOT RUN: no preset cases are configured.")
    sys.exit(2)
warm = pipeline.analyze(cases[0])
if warm.get("errors"):
    print("NOT RUN: warm-up analysis failed: " + "; ".join(warm["errors"]))
    sys.exit(2)
n = 200
start = time.perf_counter()
for i in range(n):
    result = pipeline.analyze(cases[i % len(cases)])
    if result.get("errors"):
        print("NOT RUN: case analysis returned errors: " + "; ".join(result["errors"]))
        sys.exit(2)
ms = (time.perf_counter() - start) * 1000 / n
print("Average full analysis: %.2f ms per case over %d runs" % (ms, n))
print("PASS (< 50 ms)" if ms < 50 else "SLOWER than 50 ms - do not claim <50 ms")
