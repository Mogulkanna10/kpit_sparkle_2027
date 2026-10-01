"""
Experiment Suite: Change Impact Analysis (Experiments A - E)
Covers:
- Exp A: Structural impact analysis
- Exp B: Semantic impact analysis
- Exp C: Cross-domain cascading impacts
- Exp D: False semantic similarity robustness
- Exp E: No-impact change handling (Dead code / comments)
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


def run_change_impact_experiments(runner: BenchmarkRunner, mutations_file: Path, gt_file: Path, out_dir: Path) -> pd.DataFrame:
    with open(mutations_file, "r", encoding="utf-8") as f:
        muts_data = json.load(f)
    with open(gt_file, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    mutations = [MutationRecord(**m) for m in muts_data]
    gt_map = {g["mutation_id"]: GroundTruthRecord(**g) for g in gt_data}

    # Setup all projects
    for pid in ["ADAS", "POWERTRAIN", "BATTERY_EV"]:
        runner.setup_project(pid, Path("data/projects") / pid.lower())

    impact_df, reg_df = runner.run_benchmark(mutations, gt_map, semantic_threshold=0.65)
    
    out_dir.mkdir(parents=True, exist_ok=True)
    impact_df.to_csv(out_dir / "impact_results.csv", index=False)
    print(f"[OK] Change impact experiments complete. Saved {len(impact_df)} records to {out_dir / 'impact_results.csv'}")
    return impact_df


if __name__ == "__main__":
    runner = BenchmarkRunner(seed=42)
    run_change_impact_experiments(
        runner,
        Path("data/mutations/all_mutations.json"),
        Path("data/ground_truth/all_ground_truth.json"),
        Path("reports/raw_results")
    )
