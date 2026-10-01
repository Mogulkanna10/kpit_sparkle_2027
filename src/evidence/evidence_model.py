"""
Evidence Model
Defines structured data structures for full auditable traceability and explainability.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class DecisionEvidence:
    artifact_id: str
    artifact_type: str
    decision: str  # STRUCTURAL_ACCEPT, SEMANTIC_RECOVERY, REJECT, REVIEW_REQUIRED
    stage: str  # GRAPH, SEMANTIC, SAFETY_GATE
    confidence: float
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisEvidenceReport:
    analysis_id: str
    timestamp: str
    changed_artifact_id: str
    subsystem: str
    structural_impacts_count: int
    semantic_recoveries_count: int
    rejected_candidates_count: int
    review_required_count: int
    total_impacts_count: int
    tests_selected_count: int
    safety_tests_count: int
    total_test_suite_size: int
    test_reduction_pct: float
    decisions: List[DecisionEvidence] = field(default_factory=list)
    impact_items: List[Dict[str, Any]] = field(default_factory=list)
    test_items: List[Dict[str, Any]] = field(default_factory=list)
    latency_profile: Dict[str, float] = field(default_factory=dict)
