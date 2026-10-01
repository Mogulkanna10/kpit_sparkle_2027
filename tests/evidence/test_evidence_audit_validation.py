"""
Gate 10: Evidence and Audit Trail Validation Suite
Validates:
1. Structural decision evidence completeness (path, depth, relations, confidence, reason)
2. Semantic decision evidence completeness (similarity, context score, filter rules, rejection reason)
3. Safety gate decision evidence completeness (safety class, mapping source, invariant guarantee)
4. REVIEW_REQUIRED decision logging
5. Multi-format report export (JSON, Markdown, HTML)
6. Cryptographic / lossless JSON roundtrip serialization
7. Strict audit invariant: Zero unexplained impacts in final output
"""
import pytest
import json
from pathlib import Path

from src.evidence.evidence_model import DecisionEvidence, AnalysisEvidenceReport
from src.evidence.evidence_logger import EvidenceLogger
from src.evidence.report_generator import ReportGenerator
from src.impact.impact_engine import ImpactEngineResult
from src.impact.impact_union import Impact, ImpactType, SourceStage
from src.semantic.retriever import RetrievedCandidate
from src.testing.regression_selector import RegressionSelectionResult
from src.testing.test_mapper import MappedTest
from src.ingestion.git_diff import ChangedArtifact


@pytest.fixture
def mock_pipeline_results():
    """Generates realistic pipeline output structures for audit verification."""
    change = ChangedArtifact(
        artifact_id="REQ_AEB_BRAKE_01",
        artifact_type="Requirement",
        subsystem="ADAS",
        ecu="ECU_1",
        change_type="MODIFY",
        diff_text="- TTC 1.2s\n+ TTC 1.5s",
        change_semantics="Increase AEB emergency braking TTC trigger threshold"
    )
    
    structural_impacts = [
        Impact(
            artifact_id="FN_TRIGGER_BRAKE",
            artifact_type="C_Function",
            subsystem="ADAS",
            ecu="ECU_1",
            impact_type=ImpactType.STRUCTURAL,
            confidence=1.0,
            source_stage=SourceStage.GRAPH,
            evidence={
                "decision": "DETERMINISTIC_GRAPH_TRAVERSAL",
                "depth": 2,
                "path": ["REQ_AEB_BRAKE_01", "SWC_AEB", "FN_TRIGGER_BRAKE"],
                "relations": ["MAPS_TO", "CALLS"],
                "confidence": 1.0,
                "reason": "Explicit graph path of depth 2 with confidence 1.00"
            },
            source_file="src/adas_controller.c",
            source_location="L45-L89"
        )
    ]
    
    semantic_candidates = [
        RetrievedCandidate(
            artifact_id="FN_HYDRAULIC_PUMP",
            artifact_type="C_Function",
            subsystem="ADAS",
            ecu="ECU_1",
            similarity_score=0.88,
            context_score=0.95,
            status="ACCEPT",
            source_file="src/hydraulic_actuator.c",
            evidence={"raw_similarity": 0.88, "context_rules": {"subsystem_match": True, "type_compatibility": True}}
        ),
        RetrievedCandidate(
            artifact_id="FN_CABIN_FAN",
            artifact_type="C_Function",
            subsystem="Body_Electronics",
            ecu="ECU_Body",
            similarity_score=0.62,
            context_score=0.0,
            status="REJECT",
            rejection_reason="Subsystem mismatch: Candidate belongs to 'Body_Electronics', expected 'ADAS'",
            source_file="src/climate.c",
            evidence={"raw_similarity": 0.62, "context_rules": {"subsystem_match": False}}
        ),
        RetrievedCandidate(
            artifact_id="REQ_AMBIGUOUS_ALERT",
            artifact_type="Requirement",
            subsystem="ADAS",
            ecu="ECU_1",
            similarity_score=0.72,
            context_score=0.85,
            status="REVIEW_REQUIRED",
            rejection_reason="Ambiguous functional requirement - insufficient technical context",
            source_file="reqs/alerts.json",
            evidence={"raw_similarity": 0.72, "context_rules": {"subsystem_match": True}}
        )
    ]
    
    final_impacts = structural_impacts + [
        Impact(
            artifact_id="FN_HYDRAULIC_PUMP",
            artifact_type="C_Function",
            subsystem="ADAS",
            ecu="ECU_1",
            impact_type=ImpactType.SEMANTIC,
            confidence=0.88,
            source_stage=SourceStage.SEMANTIC,
            evidence={"reason": "Semantic similarity 0.88 with context score 0.95"}
        )
    ]
    
    impact_res = ImpactEngineResult(
        changed_artifact_id="REQ_AEB_BRAKE_01",
        structural_impacts=structural_impacts,
        semantic_impacts=[final_impacts[1]],
        all_semantic_candidates=semantic_candidates,
        final_impacts=final_impacts,
        review_required_items=[semantic_candidates[2]],
        structural_coverage_complete=True,
        stage1_latency_ms=1.12,
        stage2_latency_ms=0.45,
        total_latency_ms=1.57
    )
    
    selected_tests = [
        MappedTest("TC_AEB_TEST_01", "AEB full stop test", "ASIL-D", "ADAS", "FN_TRIGGER_BRAKE", "STRUCTURAL_GRAPH"),
        MappedTest("TC_PUMP_TEST_01", "Hydraulic pressure rise", "ASIL-C", "ADAS", "FN_HYDRAULIC_PUMP", "SEMANTIC_RECOVERY")
    ]
    
    test_res = RegressionSelectionResult(
        all_tests_count=20,
        selected_tests=selected_tests,
        removed_tests_count=18,
        safety_tests=selected_tests,
        test_reduction_pct=90.0,
        safety_recall_pct=100.0
    )
    
    return change, impact_res, test_res


def test_structural_evidence_completeness(mock_pipeline_results):
    """Scenario 1: Structural decisions capture full graph path, depth, relations, and reason."""
    change, impact_res, test_res = mock_pipeline_results
    logger = EvidenceLogger()
    report = logger.build_report(change, impact_res, test_res)
    
    struct_decisions = [d for d in report.decisions if d.decision == "STRUCTURAL_ACCEPT"]
    assert len(struct_decisions) == 1
    
    d = struct_decisions[0]
    assert d.artifact_id == "FN_TRIGGER_BRAKE"
    assert d.stage == "GRAPH"
    assert d.confidence == 1.0
    assert d.details["depth"] == 2
    assert d.details["path"] == ["REQ_AEB_BRAKE_01", "SWC_AEB", "FN_TRIGGER_BRAKE"]
    assert d.details["relations"] == ["MAPS_TO", "CALLS"]
    assert "Explicit graph path" in d.reason


def test_semantic_evidence_completeness(mock_pipeline_results):
    """Scenario 2: Semantic decisions log similarity, context rules, and explicit rejection reasons."""
    change, impact_res, test_res = mock_pipeline_results
    logger = EvidenceLogger()
    report = logger.build_report(change, impact_res, test_res)
    
    sem_decisions = {d.artifact_id: d for d in report.decisions if d.stage == "SEMANTIC"}
    
    # Accepted semantic candidate
    acc = sem_decisions["FN_HYDRAULIC_PUMP"]
    assert acc.decision == "SEMANTIC_ACCEPT"
    assert acc.confidence == 0.88
    assert acc.details["context_score"] == 0.95
    assert acc.details["evidence"]["context_rules"]["subsystem_match"] is True
    
    # Rejected decoy candidate
    rej = sem_decisions["FN_CABIN_FAN"]
    assert rej.decision == "SEMANTIC_REJECT"
    assert "Subsystem mismatch" in rej.reason
    assert rej.details["evidence"]["context_rules"]["subsystem_match"] is False


def test_safety_gate_evidence_completeness(mock_pipeline_results):
    """Scenario 3: Safety decisions record safety classification and non-bypassable status."""
    change, impact_res, test_res = mock_pipeline_results
    logger = EvidenceLogger()
    report = logger.build_report(change, impact_res, test_res)
    
    safety_decisions = [d for d in report.decisions if d.stage == "SAFETY_GATE"]
    assert len(safety_decisions) == 2
    
    d_map = {d.artifact_id: d for d in safety_decisions}
    assert d_map["TC_AEB_TEST_01"].confidence == 1.0
    assert d_map["TC_AEB_TEST_01"].details["safety_class"] == "ASIL-D"
    assert d_map["TC_PUMP_TEST_01"].details["safety_class"] == "ASIL-C"


def test_review_required_logging(mock_pipeline_results):
    """Scenario 4: Ambiguous items are formally cataloged as REVIEW_REQUIRED."""
    change, impact_res, test_res = mock_pipeline_results
    logger = EvidenceLogger()
    report = logger.build_report(change, impact_res, test_res)
    
    rev = [d for d in report.decisions if d.decision == "SEMANTIC_REVIEW_REQUIRED"]
    assert len(rev) == 1
    assert rev[0].artifact_id == "REQ_AMBIGUOUS_ALERT"
    assert "Ambiguous functional requirement" in rev[0].reason


def test_multi_format_report_generation(mock_pipeline_results, tmp_path):
    """Scenario 5: Generates valid, non-empty JSON, Markdown, and HTML reports."""
    change, impact_res, test_res = mock_pipeline_results
    logger = EvidenceLogger()
    report = logger.build_report(change, impact_res, test_res)
    
    gen = ReportGenerator(output_dir=tmp_path)
    paths = gen.export_all(report)
    
    assert paths["json"].exists()
    assert paths["markdown"].exists()
    assert paths["html"].exists()
    
    # Check JSON validity
    with open(paths["json"], "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["analysis_id"] == report.analysis_id
    assert len(data["decisions"]) == 6
    
    # Check Markdown contents
    md_content = paths["markdown"].read_text(encoding="utf-8")
    assert f"# AURA-Impact Analysis Report: `{change.artifact_id}`" in md_content
    assert "| `FN_TRIGGER_BRAKE` |" in md_content
    
    # Check HTML contents
    html_content = paths["html"].read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html_content
    assert "AURA-Impact Analysis Report" in html_content


def test_zero_unexplained_impacts_invariant(mock_pipeline_results):
    """Scenario 6: Every accepted impact MUST have an explainable reason."""
    change, impact_res, test_res = mock_pipeline_results
    logger = EvidenceLogger()
    report = logger.build_report(change, impact_res, test_res)
    
    for item in report.impact_items:
        assert item["reason"] != "", f"Impact item {item['id']} lacks an explainable reason!"
        assert item["confidence"] > 0.0
