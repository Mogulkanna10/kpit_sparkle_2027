"""
Context-Aware Semantic Retrieval Engine (v2.0)
Retrieves semantic candidates and enriches them with engineering context scores.
"""
from typing import List, Dict, Any, Optional
from src.semantic.index import SemanticIndex, FAISS_AVAILABLE  # re-exported for introspection
from src.semantic.context_filter import EngineeringContextFilter


class SemanticRetriever:
    def __init__(
        self,
        index: SemanticIndex,
        context_filter: Optional[EngineeringContextFilter] = None,
        default_threshold: float = 0.65,
        default_variant: str = "VARIANT_C"
    ):
        self.index = index
        self.context_filter = context_filter
        self.default_threshold = default_threshold
        self.default_variant = default_variant

    def retrieve_candidates_for_change(
        self,
        change_text: str,
        source_artifact_id: Optional[str] = None,
        source_artifact_type: str = "Requirement",
        source_subsystem: str = "ADAS",
        threshold: Optional[float] = None,
        top_k: Optional[int] = None,
        variant: Optional[str] = None,
        project: Optional[str] = None,
        exclude_node_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        th = threshold if threshold is not None else self.default_threshold
        mode = variant if variant is not None else self.default_variant
        exclude = set(exclude_node_ids or [])
        subsystem = project if project else source_subsystem

        # 1. Embed query text → dense vector (AURA-DomainHashEmbedder-384)
        if hasattr(self.index, "embedder") and self.index.embedder is not None:
            query_vec = self.index.embedder.embed_text(change_text)
        else:
            import numpy as _np
            import hashlib as _hl
            import re as _re
            _dim = getattr(self.index, "dimension", 384)
            _vec = _np.zeros(_dim, dtype=_np.float32)
            for _tok in _re.findall(r"\b[a-z0-9_]+\b", change_text.lower()):
                _vec[int(_hl.md5(_tok.encode()).hexdigest(), 16) % _dim] += 1.0
            _n = _np.linalg.norm(_vec)
            query_vec = _vec / _n if _n > 1e-6 else _vec

        # 2. Raw Vector Index Search (collect top candidates)
        pre_top_k = (top_k * 3) if top_k else 50
        raw_tuples = self.index.search(
            query_vec=query_vec,
            top_k=pre_top_k,
            subsystem_filter=subsystem if mode != "VARIANT_A" else None,
        )
        # Normalise: index.search returns List[Tuple[IndexedArtifact, float]]
        raw_results = []
        for item, score in raw_tuples:
            raw_results.append({
                "id":         item.artifact_id,
                "name":       item.artifact_id,
                "type":       item.artifact_type,
                "project":    item.subsystem,
                "similarity": float(score),
            })

        candidates = []
        for r in raw_results:
            if r["id"] in exclude:
                continue

            raw_cos = r["similarity"]
            c_type = r["type"]
            c_subsys = r.get("project", subsystem)

            # Variant A: Semantic Only
            if mode == "VARIANT_A" or not self.context_filter:
                if raw_cos >= th:
                    candidates.append({
                        "id": r["id"],
                        "name": r["name"],
                        "node_type": c_type,
                        "semantic_score": raw_cos,
                        "context_score": 0.0,
                        "final_score": raw_cos,
                        "reason": f"Semantic cosine similarity {raw_cos:.3f} >= {th:.2f}",
                        "evidence": {"type": "RAW_SEMANTIC", "score": raw_cos}
                    })
                continue

            # Check Hard Filter if in Variant C
            if mode == "VARIANT_C":
                if not self.context_filter.passes_hard_filter(subsystem, c_subsys, c_type, raw_cos):
                    continue

            # Compute Context Score & Combined Final Score
            ctx_meta = self.context_filter.compute_context_score(
                source_artifact_id=source_artifact_id,
                source_artifact_type=source_artifact_type,
                source_subsystem=subsystem,
                candidate_id=r["id"],
                candidate_type=c_type,
                candidate_subsystem=c_subsys,
                raw_cosine=raw_cos
            )

            score_to_check = ctx_meta["final_score"]

            if score_to_check >= th:
                candidates.append({
                    "id": r["id"],
                    "name": r["name"],
                    "node_type": c_type,
                    "semantic_score": raw_cos,
                    "context_score": ctx_meta["context_score"],
                    "final_score": ctx_meta["final_score"],
                    "graph_distance": ctx_meta["graph_distance"],
                    "reason": f"Contextual score {ctx_meta['final_score']:.3f} (Cos: {raw_cos:.3f}, Ctx: {ctx_meta['context_score']:.3f}) >= {th:.2f}",
                    "evidence": {
                        "type": "CONTEXTUAL_SEMANTIC",
                        "raw_cosine": raw_cos,
                        "context_score": ctx_meta["context_score"],
                        "final_score": ctx_meta["final_score"],
                        "graph_distance": ctx_meta["graph_distance"],
                        "trace_support": ctx_meta["trace_support_score"]
                    }
                })

        # Sort descending by final score
        candidates.sort(key=lambda x: x["final_score"], reverse=True)

        limit_k = top_k if top_k is not None else 10
        candidates = candidates[:limit_k]

        return candidates
