"""
Mutation and Independent Ground Truth Generation Script
Generates >= 150 controlled automotive mutations across categories M01-M25
Generates independent, non-circular ground truth records for each mutation.
"""
import os
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.benchmark.mutation_generator import MutationGenerator
from src.benchmark.ground_truth import GroundTruthGenerator
from scripts.build_graph import build_project_graph


def main():
    base_proj_dir = Path("data/projects")
    mutations_dir = Path("data/mutations")
    ground_truth_dir = Path("data/ground_truth")

    mutations_dir.mkdir(parents=True, exist_ok=True)
    ground_truth_dir.mkdir(parents=True, exist_ok=True)

    projects = ["adas", "powertrain", "battery_ev"]
    generator = MutationGenerator(seed=2002)

    total_mutations = 0
    all_mutations_list = []
    all_gt_list = []

    for proj in projects:
        p_dir = base_proj_dir / proj
        print(f"Generating mutations & ground truth for {proj.upper()}...")
        
        eng_graph = build_project_graph(proj.upper(), p_dir)
        graph_dict = eng_graph.to_dict()

        mutations = generator.generate_mutations_for_project(proj.upper(), graph_dict)
        gt_gen = GroundTruthGenerator(eng_graph)

        for m in mutations:
            gt = gt_gen.generate_ground_truth(m)
            
            # Save individual files
            m_file = mutations_dir / f"{m.mutation_id}.json"
            gt_file = ground_truth_dir / f"{m.mutation_id}.json"

            with open(m_file, "w", encoding="utf-8") as f:
                json.dump(m.to_dict(), f, indent=2)

            with open(gt_file, "w", encoding="utf-8") as f:
                json.dump(gt.to_dict(), f, indent=2)

            all_mutations_list.append(m.to_dict())
            all_gt_list.append(gt.to_dict())
            total_mutations += 1

        print(f"  [OK] Generated {len(mutations)} mutations and ground truth records for {proj.upper()}")

    # Save summary catalogs
    with open(mutations_dir / "all_mutations.json", "w", encoding="utf-8") as f:
        json.dump(all_mutations_list, f, indent=2)

    with open(ground_truth_dir / "all_ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(all_gt_list, f, indent=2)

    print(f"\n[OK] Total controlled mutations generated: {total_mutations}")
    print(f"[OK] Independent ground truth records generated: {len(all_gt_list)}")


if __name__ == "__main__":
    main()
