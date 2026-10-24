"""Attribution stress testing across synthetic transaction streams."""
import time
import simulator
import attribution
import invariants


def run_stress_test(n=40, seed=7):
    """Run an automated stress test generating n synthetic cases with given seed.

    Args:
        n: int, number of cases to generate (default 40).
        seed: int, pseudorandom seed (default 7).

    Returns:
        dict with requested, generated, executed, passed, failed, seed, failures, and summary.
    """
    start_time = time.perf_counter()

    try:
        cases = simulator.generate_cases(n, seed)
    except Exception as exc:
        return {
            "requested": n,
            "generated": 0,
            "executed": 0,
            "passed": 0,
            "failed": n,
            "seed": seed,
            "failures": [{"case_id": "SIMULATOR_ERROR", "error": str(exc)}],
            "duration_ms": 0,
            "summary": f"Simulator crashed generating {n} cases: {exc}",
        }

    generated_count = len(cases)
    executed_count = 0
    passed_count = 0
    failures = []

    for c in cases:
        cid = c.get("case_id", "UNKNOWN")
        executed_count += 1
        try:
            attr = attribution.analyze_attribution(c)
        except Exception as exc:
            failures.append({
                "case_id": cid,
                "error": f"Attribution analysis failed: {exc}",
                "failed_checks": [],
            })
            continue

        try:
            inv = invariants.check_case_invariants(c, attr)
            if inv["passed"]:
                passed_count += 1
            else:
                failed_checks = [chk["id"] for chk in inv["checks"] if not chk["passed"]]
                failures.append({
                    "case_id": cid,
                    "error": "; ".join(inv["errors"]),
                    "failed_checks": failed_checks,
                })
        except Exception as exc:
            failures.append({
                "case_id": cid,
                "error": f"Invariant checking failed: {exc}",
                "failed_checks": [],
            })

    failed_count = executed_count - passed_count
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    summary = (
        f"Stress test executed {executed_count}/{generated_count} cases (seed {seed}): "
        f"{passed_count} passed, {failed_count} failed in {duration_ms} ms."
    )

    return {
        "requested": n,
        "generated": generated_count,
        "executed": executed_count,
        "passed": passed_count,
        "failed": failed_count,
        "seed": seed,
        "failures": failures,
        "duration_ms": duration_ms,
        "summary": summary,
    }
