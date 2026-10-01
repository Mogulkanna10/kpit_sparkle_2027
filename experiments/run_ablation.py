"""
Experiment Suite: Ablation & Sensitivity Analysis (Experiments H, I, J)
Covers:
- Exp H: Semantic threshold sensitivity (tau in [0.40, 0.85])
- Exp I: Fusion weight sensitivity (wg, ws, wc)
- Exp J: Graph traversal depth sensitivity (k in [1, 6])
- Ablation: Graph vs Embedding vs Hybrid Fixed vs Hybrid Routed
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.benchmark.runners import BenchmarkRunner
from src.benchmark.mutation_generator import MutationRecord
from src.benchmark.ground_truth import GroundTruthRecord
from src.benchmark.metrics import MetricsComputer


def run_ablation_experiments(runner: BenchmarkRunner, mutations_file: Path, gt_file: Path, out_dir: Path) -> Dict[str, pd.DataFrame]:
    with open(mutations_file, "r", encoding="utf-8") as f:
        muts_data = json.load(f)
    with open(gt_file, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    mutations = [MutationRecord(**m) for m in muts_data]
    gt_map = {g["mutation_id"]: GroundTruthRecord(**g) for g in gt_data}

    for pid in ["ADAS", "POWERTRAIN", "BATTERY_EV"]:
        runner.setup_project(pid, Path("data/projects") / pid.lower())

    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Threshold Sensitivity (Exp H)
    th_rows = []
    for th in [0.40, 0.50, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]:
        for mut in mutations:
            p_ctx = runner.projects_cache[mut.project_id]
            change = runner.detector.parse_mutation_record(mut.to_dict())
            gt = gt_map[mut.mutation_id]
            res = p_ctx["embedding"].run(change, threshold=th)
            m = MetricsComputer.compute_artifact_metrics(res["impacted_artifacts"], gt.true_impacted_artifacts)
            th_rows.append({"threshold": th, "mutation_id": mut.mutation_id, "recall": m["recall"], "precision": m["precision"], "f1": m["f1"]})
    th_df = pd.DataFrame(th_rows)
    th_df.to_csv(out_dir / "threshold_sensitivity.csv", index=False)
    print(f"[OK] Exp H: Threshold sensitivity completed ({len(th_df)} records)")

    # 2. Graph Depth Sensitivity (Exp J)
    depth_rows = []
    for d in [1, 2, 3, 4, 5, 6]:
        for mut in mutations:
            p_ctx = runner.projects_cache[mut.project_id]
            change = runner.detector.parse_mutation_record(mut.to_dict())
            gt = gt_map[mut.mutation_id]
            res = p_ctx["graph_only"].run(change, max_depth=d)
            m = MetricsComputer.compute_artifact_metrics(res["impacted_artifacts"], gt.true_impacted_artifacts)
            depth_rows.append({"depth": d, "mutation_id": mut.mutation_id, "recall": m["recall"], "precision": m["precision"], "f1": m["f1"]})
    depth_df = pd.DataFrame(depth_rows)
    depth_df.to_csv(out_dir / "depth_sensitivity.csv", index=False)
    print(f"[OK] Exp J: Depth sensitivity completed ({len(depth_df)} records)")

    # 3. Fusion Weight Sensitivity (Exp I)
    weight_configs = [
        ("Graph_Dominated", 0.70, 0.20, 0.10),
        ("Balanced", 0.50, 0.35, 0.15),
        ("Semantic_Heavy", 0.30, 0.55, 0.15),
        ("Equal_Weights", 0.33, 0.33, 0.34)
    ]
    w_rows = []
    for w_name, wg, ws, wc in weight_configs:
        for mut in mutations:
            p_ctx = runner.projects_cache[mut.project_id]
            change = runner.detector.parse_mutation_record(mut.to_dict())
            gt = gt_map[mut.mutation_id]
            g_imp = p_ctx["graph_analyzer"].analyze_impact(change)
            s_imp = p_ctx["semantic_analyzer"].analyze_impact(change, threshold=0.65)
            fused = p_ctx["fusion_engine"].fuse(g_imp, s_imp, category=p_ctx["hybrid_routed"].classifier.classify(change), wg=wg, ws=ws, wc=wc)
            ranked = p_ctx["ranker"].rank(fused, min_score_threshold=0.20)
            pred = [item["artifact_id"] for item in ranked]
            m = MetricsComputer.compute_artifact_metrics(pred, gt.true_impacted_artifacts)
            w_rows.append({"weight_config": w_name, "wg": wg, "ws": ws, "wc": wc, "mutation_id": mut.mutation_id, "recall": m["recall"], "precision": m["precision"], "f1": m["f1"]})
    w_df = pd.DataFrame(w_rows)
    w_df.to_csv(out_dir / "fusion_sensitivity.csv", index=False)
    print(f"[OK] Exp I: Fusion weight sensitivity completed ({len(w_df)} records)")

    return {"threshold": th_df, "depth": depth_df, "fusion": w_df}


if __name__ == "__main__":
    runner = BenchmarkRunner(seed=42)
    run_ablation_experiments(
        runner,
        Path("data/mutations/all_mutations.json"),
        Path("data/ground_truth/all_ground_truth.json"),
        Path("reports/raw_results")
    )
