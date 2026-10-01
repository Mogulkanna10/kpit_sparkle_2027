"""
Experiment Suite: Cross-Project Generalization (Experiment K)
Evaluates whether AURA-Impact generalizes across ADAS, Powertrain, and Battery_EV
using Leave-One-Project-Out evaluation without project-specific hardcoding.
"""
import os
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.benchmark.runners import BenchmarkRunner
from src.benchmark.mutation_generator import MutationRecord
from src.benchmark.ground_truth import GroundTruthRecord
from src.benchmark.metrics import MetricsComputer


def run_cross_project_generalization(runner: BenchmarkRunner, mutations_file: Path, gt_file: Path, out_dir: Path) -> pd.DataFrame:
    with open(mutations_file, "r", encoding="utf-8") as f:
        muts_data = json.load(f)
    with open(gt_file, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    mutations = [MutationRecord(**m) for m in muts_data]
    gt_map = {g["mutation_id"]: GroundTruthRecord(**g) for g in gt_data}

    for pid in ["ADAS", "POWERTRAIN", "BATTERY_EV"]:
        runner.setup_project(pid, Path("data/projects") / pid.lower())

    gen_rows = []
    projects = ["ADAS", "POWERTRAIN", "BATTERY_EV"]

    for held_out in projects:
        train_projects = [p for p in projects if p != held_out]
        train_muts = [m for m in mutations if m.project_id in train_projects]
        test_muts = [m for m in mutations if m.project_id == held_out]

        # 1. Calibrate threshold on training projects only
        calibrated_th = runner.calibrate_threshold(train_muts, gt_map)

        # 2. Evaluate on held-out test project
        for mut in test_muts:
            p_ctx = runner.projects_cache[mut.project_id]
            change = runner.detector.parse_mutation_record(mut.to_dict())
            gt = gt_map[mut.mutation_id]

            for m_name, fn in [
                ("Graph_Only", p_ctx["graph_only"].run),
                ("Embedding_Only", lambda c: p_ctx["embedding"].run(c, threshold=calibrated_th)),
                ("Hybrid_AURA_Routed", lambda c: p_ctx["hybrid_routed"].run(c, semantic_threshold=calibrated_th))
            ]:
                res = fn(change)
                art_m = MetricsComputer.compute_artifact_metrics(res["impacted_artifacts"], gt.true_impacted_artifacts)
                gen_rows.append({
                    "held_out_project": held_out,
                    "mutation_id": mut.mutation_id,
                    "change_type": mut.change_type,
                    "method": m_name,
                    "calibrated_threshold": calibrated_th,
                    "recall": art_m["recall"],
                    "precision": art_m["precision"],
                    "f1": art_m["f1"],
                    "latency_ms": res.get("latency_ms", 0.0)
                })

    gen_df = pd.DataFrame(gen_rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    gen_df.to_csv(out_dir / "generalization_results.csv", index=False)
    print(f"[OK] Exp K: Cross-project generalization completed ({len(gen_df)} records)")
    return gen_df


if __name__ == "__main__":
    runner = BenchmarkRunner(seed=42)
    run_cross_project_generalization(
        runner,
        Path("data/mutations/all_mutations.json"),
        Path("data/ground_truth/all_ground_truth.json"),
        Path("reports/raw_results")
    )
