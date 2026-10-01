"""
Experiment Suite: Regression Test Selection & Safety Gate Analysis (Experiments F & G)
Evaluates Test Reduction, Impacted Test Recall, Safety-Critical Recall, and False Negatives.
"""
import os
import sys
import json
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.benchmark.runners import BenchmarkRunner
from src.benchmark.mutation_generator import MutationRecord
from src.benchmark.ground_truth import GroundTruthRecord


def run_regression_experiments(runner: BenchmarkRunner, mutations_file: Path, gt_file: Path, out_dir: Path) -> pd.DataFrame:
    with open(mutations_file, "r", encoding="utf-8") as f:
        muts_data = json.load(f)
    with open(gt_file, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    mutations = [MutationRecord(**m) for m in muts_data]
    gt_map = {g["mutation_id"]: GroundTruthRecord(**g) for g in gt_data}

    for pid in ["ADAS", "POWERTRAIN", "BATTERY_EV"]:
        runner.setup_project(pid, Path("data/projects") / pid.lower())

    impact_df, reg_df = runner.run_benchmark(mutations, gt_map, semantic_threshold=0.65)
    
    out_dir.mkdir(parents=True, exist_ok=True)
    reg_df.to_csv(out_dir / "regression_results.csv", index=False)
    print(f"[OK] Regression selection experiments complete. Saved {len(reg_df)} records to {out_dir / 'regression_results.csv'}")
    return reg_df


if __name__ == "__main__":
    runner = BenchmarkRunner(seed=42)
    run_regression_experiments(
        runner,
        Path("data/mutations/all_mutations.json"),
        Path("data/ground_truth/all_ground_truth.json"),
        Path("reports/raw_results")
    )
