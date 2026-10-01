"""
Hard Context Filter
Applies deterministic engineering context constraints to eliminate false positives and distractors.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from src.semantic.index import IndexedArtifact


@dataclass
class FilterResult:
    passed: bool
    context_score: float
    rejection_reason: str = ""
    applied_rules: Dict[str, bool] = None


class ContextFilter:
    """Evaluates candidates against hard automotive engineering constraints."""

    def __init__(self,
                 enforce_subsystem: bool = True,
                 enforce_artifact_type: bool = True,
                 min_context_score: float = 0.50,
                 eng_graph: Any = None,
                 **kwargs):
        self.enforce_subsystem = enforce_subsystem
        self.enforce_artifact_type = enforce_artifact_type
        self.min_context_score = min_context_score
        self.eng_graph = eng_graph

    def evaluate(self, candidate: IndexedArtifact, query_context: Dict[str, Any]) -> FilterResult:
        rules = {}
        target_subsystem = query_context.get("subsystem", "")
        source_type = query_context.get("artifact_type", "Requirement")

        # 1. Subsystem Domain Isolation (Rule 1)
        if self.enforce_subsystem and target_subsystem:
            c_sub = candidate.subsystem.lower().replace("_", "").replace(" ", "")
            q_sub = target_subsystem.lower().replace("_", "").replace(" ", "")
            if c_sub != q_sub and q_sub not in c_sub and c_sub not in q_sub:
                return FilterResult(
                    passed=False,
                    context_score=0.0,
                    rejection_reason=f"Subsystem mismatch: Candidate belongs to '{candidate.subsystem}', expected '{target_subsystem}'",
                    applied_rules={"subsystem_match": False}
                )
            rules["subsystem_match"] = True
        else:
            rules["subsystem_match"] = True

        # 2. Artifact Type Compatibility (Rule 2)
        # Requirement changes map to functional implementations (C_Function, Runnable, SWC, Interface)
        if self.enforce_artifact_type:
            c_type = candidate.artifact_type.lower()
            valid_targets = ["c_function", "runnable", "softwarecomponent", "swc", "interface", "dataelement", "requirement"]
            if not any(v in c_type for v in valid_targets):
                return FilterResult(
                    passed=False,
                    context_score=0.2,
                    rejection_reason=f"Incompatible target artifact type: '{candidate.artifact_type}'",
                    applied_rules={"type_compatibility": False}
                )
            rules["type_compatibility"] = True

        # 3. Interface & Domain Scoring
        score = 0.80
        if rules.get("subsystem_match", False):
            score += 0.15
        if rules.get("type_compatibility", False):
            score += 0.05

        return FilterResult(
            passed=(score >= self.min_context_score),
            context_score=min(1.0, score),
            rejection_reason="",
            applied_rules=rules
        )

    def passes_hard_filter(
            self,
            source_subsystem: str,
            candidate_subsystem: str,
            candidate_type: str,
            raw_cosine: float
    ) -> bool:
        """
        Hard subsystem isolation gate (VARIANT_C).
        Returns False only when candidate is clearly out-of-domain.
        """
        if self.enforce_subsystem and source_subsystem and candidate_subsystem:
            s1 = source_subsystem.lower().replace("_", "").replace(" ", "")
            s2 = candidate_subsystem.lower().replace("_", "").replace(" ", "")
            if s1 != s2 and s1 not in s2 and s2 not in s1:
                return False
        return True

    def compute_context_score(self,
                              source_artifact_id: str = "",
                              source_artifact_type: str = "",
                              source_subsystem: str = "",
                              candidate_id: str = "",
                              candidate_type: str = "",
                              candidate_subsystem: str = "",
                              raw_cosine: float = 0.5,
                              **kwargs) -> Dict[str, Any]:
        score = raw_cosine
        if source_subsystem and candidate_subsystem and source_subsystem.lower() == candidate_subsystem.lower():
            score += 0.15
        else:
            score -= 0.30
        score = max(0.0, min(1.0, score))
        # Estimate graph distance via eng_graph if available
        graph_distance = -1
        if self.eng_graph is not None:
            try:
                import networkx as nx
                if source_artifact_id and candidate_id:
                    try:
                        graph_distance = nx.shortest_path_length(
                            self.eng_graph.graph, source_artifact_id, candidate_id
                        )
                    except (nx.NetworkXNoPath, nx.NodeNotFound):
                        graph_distance = 99
            except Exception:
                graph_distance = -1
        return {
            "context_score":      score,
            "final_score":        score,
            "passed":             score >= 0.5,
            "applied_rules":      {},
            "graph_distance":     graph_distance,
            "trace_support_score": min(1.0, score + 0.1),
        }


# Backward-compatible alias
EngineeringContextFilter = ContextFilter
