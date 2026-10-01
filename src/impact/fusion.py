"""
Impact Fusion Engine (Architecture B Canonical)
Implements strict set union S_final = S_struct UNION S_semantic.
Ensures that all deterministic structural impacts and all context-constrained
semantic fallback candidates are included in the final impact set without
exclusion via weighted score attenuation.
"""
from typing import Dict, List, Any, Optional
from src.impact.change_classifier import ChangeCategory


class ImpactFusionEngine:
    def __init__(self, wg: float = 0.55, ws: float = 0.30, wc: float = 0.15, mode: str = "strict_union"):
        # Retain weights for backward-compatibility / historical inspection
        self.wg = wg
        self.ws = ws
        self.wc = wc
        self.mode = mode

    def fuse(
        self,
        graph_impacts: Dict[str, Dict[str, Any]],
        semantic_impacts: Dict[str, Dict[str, Any]],
        category: ChangeCategory = ChangeCategory.MIXED,
        wg: Optional[float] = None,
        ws: Optional[float] = None,
        wc: Optional[float] = None,
        mode: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        w_g = wg if wg is not None else self.wg
        w_s = ws if ws is not None else self.ws
        w_c = wc if wc is not None else self.wc
        active_mode = mode if mode is not None else self.mode

        all_node_ids = set(graph_impacts.keys()).union(set(semantic_impacts.keys()))
        fused: Dict[str, Dict[str, Any]] = {}

        for node_id in all_node_ids:
            g_data = graph_impacts.get(node_id)
            s_data = semantic_impacts.get(node_id)

            g_score = g_data["structural_score"] if g_data else 0.0
            s_score = s_data["final_score"] if (s_data and "final_score" in s_data) else (s_data["semantic_score"] if s_data else 0.0)
            raw_cosine = s_data["semantic_score"] if s_data else 0.0
            ctx_score = s_data.get("context_score", 0.0) if s_data else 0.0

            # Context boost C
            if g_data and s_data:
                c_score = 1.0
                reason = "Dual confirmation: Reachable in engineering graph and high contextual relevance"
            elif g_data:
                c_score = 0.85
                dist = g_data.get("distance", 0)
                reason = f"Deterministic structural dependency at distance {dist}"
            else:
                c_score = 0.60
                reason = f"Contextual semantic candidate (Score: {s_score:.3f}, Cos: {raw_cosine:.3f})"

            if category == ChangeCategory.NO_IMPACT:
                final_score = 0.0
                reason = "Change classified as NO_IMPACT (dead code / comment / formatting)"
            elif active_mode == "strict_union":
                # Architecture B Strict Set Union:
                # S_final = S_struct UNION S_semantic
                # Any node from structural or semantic fallback is retained without score attenuation
                if g_data and s_data:
                    final_score = max(g_score, s_score, (w_g * g_score) + (w_s * s_score) + (w_c * c_score))
                elif g_data:
                    final_score = g_score
                else:
                    final_score = s_score
            else:
                # Legacy weighted mode
                if category == ChangeCategory.STRUCTURAL:
                    final_score = g_score if g_data else (0.05 * s_score)
                elif category == ChangeCategory.SEMANTIC:
                    final_score = (0.35 * g_score) + (0.50 * s_score) + (0.15 * c_score)
                else:
                    final_score = (w_g * g_score) + (w_s * s_score) + (w_c * c_score)

            confidence = 1.0 if (g_data and g_data.get("distance", 0) <= 2) else (0.85 if g_data else 0.70)
            node_type = (g_data.get("node_type") if g_data else None) or (s_data.get("node_type") if s_data else "Unknown")

            fused[node_id] = {
                "id": node_id,
                "node_type": node_type,
                "impact_score": float(final_score),
                "confidence": float(confidence),
                "graph_evidence": g_data.get("evidence", []) if g_data else [],
                "graph_distance": g_data.get("distance", -1) if g_data else (s_data.get("graph_distance", -1) if s_data else -1),
                "semantic_evidence": s_data.get("evidence", {}) if s_data else {},
                "semantic_score": raw_cosine,
                "context_score": ctx_score,
                "structural_score": g_score,
                "selection_reason": reason
            }

        return fused
