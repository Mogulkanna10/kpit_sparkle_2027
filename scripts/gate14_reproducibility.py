"""
scripts/gate14_reproducibility.py
Gate 14 — Reproducibility Audit

Executes the canonical benchmark TWICE under identical conditions and saves:
  artifacts/reproducibility_run_1.json
  artifacts/reproducibility_run_2.json

Consumed by tests/benchmark/test_reproducibility.py (18 tests).
"""
import io
import sys
import json
import hashlib
import platform
import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from benchmark.final.config import (
    VERSION, MASTER_SEED, CANONICAL_SEMANTIC_THRESHOLD,
    CANONICAL_UNION_MODE, CANONICAL_MODEL_NAME,
)

OUTPUT_DIR = ROOT_DIR / "benchmark" / "final" / "outputs"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
GATES_DIR = ARTIFACTS_DIR / "gates"


# Columns that vary due to wall-clock time and must be excluded from deterministic hashes
_TIMING_COLS = {
    "latency_ms", "query_ms", "graph_build_ms", "peak_memory_mb",
    "latency_ms_mean", "latency_ms_std", "latency_ms_min", "latency_ms_max",
}


def _sha256_csv_deterministic(path: Path) -> str:
    """SHA-256 of a CSV's data columns, excluding wall-clock timing columns.
    This ensures two runs with identical data but different execution times
    produce identical hashes.
    """
    if not path.exists():
        return "MISSING"
    df = pd.read_csv(path)
    # Drop any timing-only columns that are present
    cols_to_drop = [c for c in df.columns if c in _TIMING_COLS]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return hashlib.sha256(buf.getvalue()).hexdigest()


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=ROOT_DIR
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def _run_single(run_number: int) -> dict:
    print(f"\n{'='*60}")
    print(f"  Gate 14 Reproducibility Run {run_number}")
    print(f"{'='*60}\n")

    from benchmark.final.runner import run as _run
    artifact = _run()

    csv_hashes = {}
    for name, rel in [
        ("impact_results_csv",     "impact_results.csv"),
        ("regression_results_csv", "regression_results.csv"),
        ("semantic_results_csv",   "semantic_results.csv"),
        ("summary_table_csv",      "summary_table.csv"),
    ]:
        fpath = OUTPUT_DIR / rel
        csv_hashes[name] = _sha256_csv_deterministic(fpath)

    record = {
        "run_number":         run_number,
        "git_commit":         _git_commit(),
        "python_version":     platform.python_version(),
        "n_mutations":        artifact.get("n_mutations", 150),
        "timestamp":          datetime.now(timezone.utc).isoformat(),
        "dataset_fingerprint": artifact.get("dataset_fingerprint", ""),
        "canonical_threshold": round(CANONICAL_SEMANTIC_THRESHOLD, 4),
        "union_mode":          CANONICAL_UNION_MODE,
        "model":               CANONICAL_MODEL_NAME,
        "embedding_dimension": 384,
        "seed":                MASTER_SEED,
        "metrics":             artifact.get("metrics", {}),
        "safety":              artifact.get("safety", {}),
        "semantic":            artifact.get("semantic", {}),
        "statistics":          artifact.get("statistics", {}),
        "deterministic_hashes": csv_hashes,
        "version":             VERSION,
    }
    return record


def main():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    GATES_DIR.mkdir(parents=True, exist_ok=True)

    run1 = _run_single(1)
    out1 = ARTIFACTS_DIR / "reproducibility_run_1.json"
    out1.write_text(json.dumps(run1, indent=2), encoding="utf-8")
    print(f"\n[Gate-14] Run 1 saved: {out1}")

    run2 = _run_single(2)
    out2 = ARTIFACTS_DIR / "reproducibility_run_2.json"
    out2.write_text(json.dumps(run2, indent=2), encoding="utf-8")
    print(f"[Gate-14] Run 2 saved: {out2}")

    checks = [
        ("dataset_fingerprint",
            run1["dataset_fingerprint"] == run2["dataset_fingerprint"]),
        ("canonical_threshold",
            run1["canonical_threshold"] == run2["canonical_threshold"]),
        ("impact CSV hash",
            run1["deterministic_hashes"]["impact_results_csv"] ==
            run2["deterministic_hashes"]["impact_results_csv"]),
        ("regression CSV hash",
            run1["deterministic_hashes"]["regression_results_csv"] ==
            run2["deterministic_hashes"]["regression_results_csv"]),
        ("AURA recall",
            run1["metrics"].get("aura_hybrid_routed", {}).get("artifact_recall") ==
            run2["metrics"].get("aura_hybrid_routed", {}).get("artifact_recall")),
        ("graph recall",
            run1["metrics"].get("graph_only", {}).get("artifact_recall") ==
            run2["metrics"].get("graph_only", {}).get("artifact_recall")),
        ("safety pass_count",
            run1["safety"].get("pass_count") == run2["safety"].get("pass_count")),
    ]

    all_ok = all(ok for _, ok in checks)
    print("\n[Gate-14] Determinism verification:")
    for label, ok in checks:
        status = "MATCH" if ok else "MISMATCH"
        print(f"  {label:<42} {status}")

    aura_r1 = run1["metrics"].get("aura_hybrid_routed", {}).get("artifact_recall", 0.0)
    aura_r2 = run2["metrics"].get("aura_hybrid_routed", {}).get("artifact_recall", 0.0)
    graph_r  = run1["metrics"].get("graph_only", {}).get("artifact_recall", 0.0)

    gate_evidence = {
        "gate":  "GATE-14",
        "title": "Reproducibility Audit",
        "status": "PASS" if all_ok else "FAIL",
        "git_commit":          run1["git_commit"],
        "python_version":      run1["python_version"],
        "seed":                MASTER_SEED,
        "canonical_threshold": CANONICAL_SEMANTIC_THRESHOLD,
        "union_mode":          CANONICAL_UNION_MODE,
        "model":               CANONICAL_MODEL_NAME,
        "n_mutations":         run1["n_mutations"],
        "dataset_fingerprint_run1": run1["dataset_fingerprint"],
        "dataset_fingerprint_run2": run2["dataset_fingerprint"],
        "determinism_checks":       {l: o for l, o in checks},
        "all_determinism_checks_pass": all_ok,
        "aura_recall_run1": aura_r1,
        "aura_recall_run2": aura_r2,
        "graph_recall_run1": graph_r,
        "aura_gt_graph": aura_r1 > graph_r,
        "safety_pass_count": run1["safety"].get("pass_count", 0),
        "safety_total":      run1["safety"].get("total", 0),
        "impact_csv_hash_run1": run1["deterministic_hashes"]["impact_results_csv"],
        "impact_csv_hash_run2": run2["deterministic_hashes"]["impact_results_csv"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    gate_path = GATES_DIR / "stage_14_gate.json"
    gate_path.write_text(json.dumps(gate_evidence, indent=2), encoding="utf-8")

    print(f"\n[Gate-14] Gate evidence: {gate_path}")
    print(f"\n{'='*60}")
    print(f"  Gate 14 Status: {gate_evidence['status']}")
    print(f"  AURA recall: {aura_r1:.4f}  |  Graph recall: {graph_r:.4f}")
    print(f"  AURA > Graph: {aura_r1 > graph_r}")
    print(f"{'='*60}")

    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
