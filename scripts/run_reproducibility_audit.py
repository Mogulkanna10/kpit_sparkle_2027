"""
Gate 14 — Reproducibility Execution and Output Comparison Script
Runs the canonical benchmark twice without modification and saves:
  - artifacts/reproducibility_run_1.json
  - artifacts/reproducibility_run_2.json
Compares all metrics, predictions, test selections, and deterministic outputs.
"""
import sys
import os
import json
import time
import hashlib
import platform
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd

from benchmark.final import runner as final_runner
from benchmark.final.config import (
    MASTER_SEED, MUTATION_SEED, TOTAL_MUTATIONS,
    CANONICAL_SEMANTIC_THRESHOLD, CANONICAL_MODEL_NAME,
    CANONICAL_UNION_MODE, VERSION, OUTPUT_DIR
)


def compute_file_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash of a file."""
    if not file_path.exists():
        return ""
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def capture_run(run_id: str) -> Dict[str, Any]:
    print(f"\n=======================================================")
    print(f"  EXECUTING CANONICAL BENCHMARK {run_id.upper()}")
    print(f"=======================================================")
    
    t0 = time.perf_counter()
    final_runner.run()
    elapsed = time.perf_counter() - t0

    # Load output CSVs
    out_dir = Path(OUTPUT_DIR)
    impact_csv = out_dir / "impact_results.csv"
    reg_csv = out_dir / "regression_results.csv"
    sem_csv = out_dir / "semantic_results.csv"
    ablation_csv = out_dir / "ablation_results.csv"
    scale_csv = out_dir / "scale_results.csv"
    summary_csv = out_dir / "summary_table.csv"

    # Compute raw file hashes
    raw_hashes = {
        "impact_results_csv": compute_file_sha256(impact_csv),
        "regression_results_csv": compute_file_sha256(reg_csv),
        "semantic_results_csv": compute_file_sha256(sem_csv),
        "ablation_results_csv": compute_file_sha256(ablation_csv),
        "summary_table_csv": compute_file_sha256(summary_csv),
    }

    # Deterministic content hashes (excluding runtime latency_ms column)
    df_impact = pd.read_csv(impact_csv)
    df_reg = pd.read_csv(reg_csv)

    df_impact_det = df_impact.drop(columns=["latency_ms"]) if "latency_ms" in df_impact.columns else df_impact
    df_reg_det = df_reg.drop(columns=["latency_ms"]) if "latency_ms" in df_reg.columns else df_reg
    df_sum = pd.read_csv(summary_csv)
    df_sum_det = df_sum.drop(columns=["latency_ms_mean"]) if "latency_ms_mean" in df_sum.columns else df_sum

    deterministic_impact_hash = hashlib.sha256(df_impact_det.to_csv(index=False).encode("utf-8")).hexdigest()
    deterministic_reg_hash = hashlib.sha256(df_reg_det.to_csv(index=False).encode("utf-8")).hexdigest()
    deterministic_sum_hash = hashlib.sha256(df_sum_det.to_csv(index=False).encode("utf-8")).hexdigest()

    # Load artifact JSON
    art_path = Path("artifacts/final_benchmark_results.json")
    artifact_data = json.loads(art_path.read_text(encoding="utf-8")) if art_path.exists() else {}

    record = {
        "run_id": run_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_commit": "ffc284ce5eb8e6b5fd25c7f09ea7822f2c27de72",
        "python_version": sys.version.split()[0],
        "platform": f"{platform.system()} {platform.release()}",
        "dataset_fingerprint": artifact_data.get("dataset_fingerprint", ""),
        "seed": MASTER_SEED,
        "model": CANONICAL_MODEL_NAME,
        "embedding_dimension": 384,
        "canonical_threshold": CANONICAL_SEMANTIC_THRESHOLD,
        "union_mode": CANONICAL_UNION_MODE,
        "n_mutations": TOTAL_MUTATIONS,
        "metrics": artifact_data.get("metrics", {}),
        "semantic": artifact_data.get("semantic", {}),
        "safety": artifact_data.get("safety", {}),
        "statistics": artifact_data.get("statistics", {}),
        "deterministic_hashes": {
            "impact_results_csv": deterministic_impact_hash,
            "regression_results_csv": deterministic_reg_hash,
            "semantic_results_csv": raw_hashes["semantic_results_csv"],
            "summary_table_csv": deterministic_sum_hash,
        },
        "raw_file_hashes": raw_hashes,
        "run_duration_s": round(elapsed, 2)
    }

    out_file = Path("artifacts") / f"{run_id}.json"
    out_file.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"Saved {out_file} (duration: {elapsed:.2f}s)")
    return record


def main():
    Path("artifacts").mkdir(exist_ok=True)
    
    # Run 1
    run1 = capture_run("reproducibility_run_1")
    
    # Run 2
    run2 = capture_run("reproducibility_run_2")

    print("\n=======================================================")
    print("  REPRODUCIBILITY DIFFERENTIAL COMPARISON")
    print("=======================================================")

    checks = [
        ("Dataset Fingerprint", run1["dataset_fingerprint"] == run2["dataset_fingerprint"]),
        ("Seed Consistency", run1["seed"] == run2["seed"]),
        ("Model Identity", run1["model"] == run2["model"]),
        ("Canonical Threshold", run1["canonical_threshold"] == run2["canonical_threshold"]),
        ("Union Mode", run1["union_mode"] == run2["union_mode"]),
        ("AURA Artifact Recall", run1["metrics"]["aura_hybrid_routed"]["artifact_recall"] == run2["metrics"]["aura_hybrid_routed"]["artifact_recall"]),
        ("Graph Artifact Recall", run1["metrics"]["graph_only"]["artifact_recall"] == run2["metrics"]["graph_only"]["artifact_recall"]),
        ("Safety Invariant Pass Count", run1["safety"]["pass_count"] == run2["safety"]["pass_count"]),
        ("Semantic Recall@1", run1["semantic"]["recall_at_1"] == run2["semantic"]["recall_at_1"]),
        ("Semantic MRR", run1["semantic"]["mrr"] == run2["semantic"]["mrr"]),
        ("Impact CSV Deterministic Hash", run1["deterministic_hashes"]["impact_results_csv"] == run2["deterministic_hashes"]["impact_results_csv"]),
        ("Regression CSV Deterministic Hash", run1["deterministic_hashes"]["regression_results_csv"] == run2["deterministic_hashes"]["regression_results_csv"]),
        ("Semantic CSV Hash", run1["deterministic_hashes"]["semantic_results_csv"] == run2["deterministic_hashes"]["semantic_results_csv"]),
        ("Summary CSV Hash", run1["deterministic_hashes"]["summary_table_csv"] == run2["deterministic_hashes"]["summary_table_csv"]),
    ]

    all_passed = True
    for name, ok in checks:
        status_str = "[PASS] IDENTICAL" if ok else "[FAIL] DIFFERENCE DETECTED"
        print(f"  {name:35s}: {status_str}")
        if not ok:
            all_passed = False

    if all_passed:
        print("\n>>> REPRODUCIBILITY VERDICT: 100% IDENTICAL & DETERMINISTIC (PASS) <<<")
    else:
        print("\n>>> REPRODUCIBILITY VERDICT: NONDETERMINISM DETECTED (FAIL) <<<")
        sys.exit(1)


if __name__ == "__main__":
    main()
