"""
Evidence Logger & Decision Tracker
Records step-by-step reasoning for structural, semantic, and safety decisions.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.evidence.evidence_model import DecisionEvidence, AnalysisEvidenceReport
from src.impact.impact_engine import ImpactEngineResult
from src.testing.regression_selector import RegressionSelectionResult
from src.ingestion.git_diff import ChangedArtifact


class EvidenceLogger:
    """Collects and aggregates audit-ready evidence across the entire analysis pipeline."""

    def __init__(self):
        self.decisions: List[DecisionEvidence] = []

    def log_decision(self,
                     artifact_id: str,
                     artifact_type: str,
                     decision: str,
                     stage: str,
                     confidence: float,
                     reason: str,
                     details: Optional[Dict[str, Any]] = None):
        self.decisions.append(DecisionEvidence(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            decision=decision,
            stage=stage,
            confidence=confidence,
            reason=reason,
            details=details or {}
        ))

    def build_report(self,
                     change: ChangedArtifact,
                     impact_res: ImpactEngineResult,
                     test_res: RegressionSelectionResult) -> AnalysisEvidenceReport:
        # Log structural impacts
        for imp in impact_res.structural_impacts:
            self.log_decision(
                artifact_id=imp.artifact_id,
                artifact_type=imp.artifact_type,
                decision="STRUCTURAL_ACCEPT",
                stage="GRAPH",
                confidence=imp.confidence,
                reason=imp.evidence.get("reason", "Deterministic graph reachability"),
                details=imp.evidence
            )

        # Log semantic candidates
        for c in impact_res.all_semantic_candidates:
            self.log_decision(
                artifact_id=c.artifact_id,
                artifact_type=c.artifact_type,
                decision=f"SEMANTIC_{c.status}",
                stage="SEMANTIC",
                confidence=c.similarity_score,
                reason=c.rejection_reason or f"Semantic similarity {c.similarity_score:.2f}",
                details={"context_score": c.context_score, "evidence": c.evidence}
            )

        # Log safety tests
        for t in test_res.safety_tests:
            self.log_decision(
                artifact_id=t.test_id,
                artifact_type="Test",
                decision="SAFETY_GATE_RETAIN",
                stage="SAFETY_GATE",
                confidence=1.0,
                reason=f"Mandatory safety-critical test ({t.safety_class})",
                details={"safety_class": t.safety_class, "source": t.mapping_source}
            )

        impact_items = [{
            "id": imp.artifact_id,
            "type": imp.artifact_type,
            "stage": imp.source_stage.value if hasattr(imp.source_stage, "value") else str(imp.source_stage),
            "confidence": imp.confidence,
            "reason": imp.evidence.get("reason", "")
        } for imp in impact_res.final_impacts]

        test_items = [{
            "id": t.test_id,
            "description": t.description,
            "safety_class": t.safety_class,
            "source": t.mapping_source
        } for t in test_res.selected_tests]

        return AnalysisEvidenceReport(
            analysis_id=f"ANALYSIS_{change.artifact_id}_{int(datetime.now().timestamp())}",
            timestamp=datetime.now().isoformat(),
            changed_artifact_id=change.artifact_id,
            subsystem=change.subsystem,
            structural_impacts_count=len(impact_res.structural_impacts),
            semantic_recoveries_count=len(impact_res.semantic_impacts),
            rejected_candidates_count=len([c for c in impact_res.all_semantic_candidates if c.status == "REJECT"]),
            review_required_count=len(impact_res.review_required_items),
            total_impacts_count=len(impact_res.final_impacts),
            tests_selected_count=len(test_res.selected_tests),
            safety_tests_count=len(test_res.safety_tests),
            total_test_suite_size=test_res.all_tests_count,
            test_reduction_pct=test_res.test_reduction_pct,
            decisions=self.decisions,
            impact_items=impact_items,
            test_items=test_items,
            latency_profile={
                "stage1_graph_ms": impact_res.stage1_latency_ms,
                "stage2_semantic_ms": impact_res.stage2_latency_ms,
                "total_ms": impact_res.total_latency_ms
            }
        )
