"""
Semantic Retrieval Evaluation & Error Diagnostic Suite (v2.0)
Calculates Recall@K, MRR, Context Score distributions, and generates debugging views.
"""
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from pathlib import Path
from src.benchmark.mutation_generator import MutationRecord
from src.benchmark.ground_truth import GroundTruthRecord
from src.benchmark.runners import BenchmarkRunner


class SemanticEvaluator:
    def __init__(self, runner: BenchmarkRunner):
        self.runner = runner

    def evaluate_semantic_mutations(
        self,
        mutations: List[MutationRecord],
        ground_truth_map: Dict[str, GroundTruthRecord]
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        semantic_muts = [m for m in mutations if m.change_type in ["M03", "M04", "M05", "M19", "M23"]]

        semantic_rows = []
        error_rows = []

        k_hits = {1: 0, 3: 0, 5: 0, 10: 0}
        reciprocal_ranks = []
        total_eval = 0

        for mut in semantic_muts:
            p_ctx = self.runner.projects_cache.get(mut.project_id)
            if not p_ctx:
                continue

            gt = ground_truth_map.get(mut.mutation_id)
            if not gt:
                continue

            query_text = mut.after_state if mut.after_state else mut.intended_change_semantics
            target_id = mut.target_node_id
            true_targets = set(gt.true_impacted_artifacts)

            # Retrieve top 10 with contextual filter (VARIANT_C)
            candidates = p_ctx["retriever"].retrieve_candidates_for_change(
                change_text=query_text,
                source_artifact_id=target_id,
                source_artifact_type=mut.artifact_type,
                source_subsystem=mut.project_id,
                threshold=0.0,  # collect full ranking
                top_k=10,
                variant="VARIANT_C"
            )

            cand_ids = [c["id"] for c in candidates]
            raw_scores = [c["semantic_score"] for c in candidates]
            ctx_scores = [c.get("context_score", 0.0) for c in candidates]
            final_scores = [c["final_score"] for c in candidates]

            # Find rank of target
            rank = -1
            for idx, cid in enumerate(cand_ids):
                if cid == target_id or cid in true_targets:
                    rank = idx + 1
                    break

            # Update Recall@K
            for k in [1, 3, 5, 10]:
                if rank > 0 and rank <= k:
                    k_hits[k] += 1

            if rank > 0:
                reciprocal_ranks.append(1.0 / rank)
            else:
                reciprocal_ranks.append(0.0)

            total_eval += 1

            semantic_rows.append({
                "mutation_id": mut.mutation_id,
                "change_type": mut.change_type,
                "project": mut.project_id,
                "query": query_text[:80],
                "true_target": target_id,
                "rank1": rank == 1,
                "rank3": rank > 0 and rank <= 3,
                "rank5": rank > 0 and rank <= 5,
                "rank10": rank > 0 and rank <= 10,
                "rank_true_target": rank if rank > 0 else ">10",
                "MRR": round(1.0 / rank, 4) if rank > 0 else 0.0,
                "top_candidate": cand_ids[0] if cand_ids else "None",
                "top_raw_cosine": raw_scores[0] if raw_scores else 0.0,
                "top_context_score": ctx_scores[0] if ctx_scores else 0.0,
                "top_final_score": final_scores[0] if final_scores else 0.0
            })

            # Error diagnosis if target missed in top 5
            if rank == -1 or rank > 5:
                # Classify error reason
                if mut.change_type == "M19":
                    reason = "Misleading similarity distractor"
                elif not p_ctx["graph"].has_node(target_id):
                    reason = "Target node not in graph"
                elif cand_ids and p_ctx["graph"].get_node(cand_ids[0]).type != p_ctx["graph"].get_node(target_id).type:
                    reason = "Artifact type competition"
                else:
                    reason = "Lexical / semantic vocabulary shift"

                error_rows.append({
                    "mutation_id": mut.mutation_id,
                    "change_type": mut.change_type,
                    "project": mut.project_id,
                    "target_id": target_id,
                    "target_type": mut.artifact_type,
                    "rank": rank if rank > 0 else ">10",
                    "error_classification": reason,
                    "top_candidates_retrieved": cand_ids[:5],
                    "query_snippet": query_text[:100]
                })

        metrics_summary = {
            "total_semantic_mutations": total_eval,
            "Recall@1": round(k_hits[1] / max(1, total_eval), 4),
            "Recall@3": round(k_hits[3] / max(1, total_eval), 4),
            "Recall@5": round(k_hits[5] / max(1, total_eval), 4),
            "Recall@10": round(k_hits[10] / max(1, total_eval), 4),
            "MRR": round(float(np.mean(reciprocal_ranks)), 4) if reciprocal_ranks else 0.0
        }

        df_sem = pd.DataFrame(semantic_rows)
        df_err = pd.DataFrame(error_rows)

        return df_sem, df_err, metrics_summary
