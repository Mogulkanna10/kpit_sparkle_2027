"""
tests/unit/test_ingestion_and_provenance.py
Dedicated behavioral unit tests for:
- ArtifactLoader (src.ingestion.artifact_loader)
- GitDiffParser (src.ingestion.git_diff)
- ProvenanceTracker (src.graph.provenance)
- RegressionSelector (src.testing.selector)
"""
import pytest
import json
from pathlib import Path
from src.ingestion.artifact_loader import ArtifactLoader
from src.ingestion.git_diff import GitDiffParser, ChangedArtifact
from src.graph.provenance import ProvenanceTracker
from src.graph.traversal import TraversalImpact
from src.graph.builder import EngineeringGraph
from src.graph.schema import GraphNode, NodeType, SafetyLevel
from src.testing.selector import RegressionSelector, SafetyGateViolationException
from src.testing.test_mapper import TestMapper
from src.testing.safety_gate import SafetyGate
from src.parsers.test_parser import TestRecord


def test_artifact_loader_behavior(tmp_path):
    (tmp_path / "swc.arxml").write_text("<AUTOSAR/>", encoding="utf-8")
    (tmp_path / "engine_ctrl.c").write_text("void step() {}", encoding="utf-8")
    (tmp_path / "req_spec_01.json").write_text('{"id": "REQ-1"}', encoding="utf-8")
    (tmp_path / "test_suite_brake.json").write_text('{"tests": []}', encoding="utf-8")

    loader = ArtifactLoader(tmp_path)
    scanned = loader.scan()

    assert len(scanned["arxml"]) == 1
    assert len(scanned["c_source"]) == 1
    assert len(scanned["requirements"]) == 1
    assert len(scanned["tests"]) == 1

    with pytest.raises(FileNotFoundError):
        ArtifactLoader(Path("non_existent_directory_xyz_123")).scan()


def test_impact_union_strict_set_union():
    from src.impact.impact_union import Impact, ImpactUnion, ImpactType, SourceStage
    s1 = Impact("A", "C_FUNCTION", "ADAS", "ECU_1", ImpactType.STRUCTURAL, 1.0, SourceStage.GRAPH)
    s2 = Impact("B", "C_FUNCTION", "ADAS", "ECU_1", ImpactType.STRUCTURAL, 1.0, SourceStage.GRAPH)
    sem1 = Impact("B", "C_FUNCTION", "ADAS", "ECU_1", ImpactType.SEMANTIC, 0.8, SourceStage.SEMANTIC)
    sem2 = Impact("C", "C_FUNCTION", "ADAS", "ECU_1", ImpactType.SEMANTIC, 0.85, SourceStage.SEMANTIC)

    union_res = ImpactUnion.compute_union([s1, s2], [sem1, sem2])
    ids = {imp.artifact_id for imp in union_res}
    assert ids == {"A", "B", "C"}
    # Structural takes precedence for duplicate key B
    b_imp = next(imp for imp in union_res if imp.artifact_id == "B")
    assert b_imp.source_stage == SourceStage.GRAPH
    assert b_imp.confidence == 1.0


def test_git_diff_parser_json(tmp_path):
    change_json = tmp_path / "change.json"
    change_json.write_text(json.dumps({
        "changes": [
            {
                "artifact_id": "REQ_001",
                "artifact_type": "Requirement",
                "project": "ADAS",
                "ecu": "ECU_RADAR",
                "change_type": "MODIFY",
                "diff_text": "- 50ms\n+ 30ms",
                "change_semantics": "Tighter latency tolerance"
            }
        ]
    }), encoding="utf-8")

    artifacts = GitDiffParser.parse_change_file(change_json)
    assert len(artifacts) == 1
    assert artifacts[0].artifact_id == "REQ_001"
    assert artifacts[0].subsystem == "ADAS"
    assert artifacts[0].change_type == "MODIFY"


def test_git_diff_parser_missing_file():
    with pytest.raises(FileNotFoundError):
        GitDiffParser.parse_change_file(Path("missing_change_file.json"))


def test_provenance_tracker_format_and_mermaid():
    g = EngineeringGraph()
    g.add_node(GraphNode(id="A", type=NodeType.REQUIREMENT, source_file="spec.json"))
    g.add_node(GraphNode(id="B", type=NodeType.C_FUNCTION, source_file="ctrl.c"))

    impact = TraversalImpact(
        artifact_id="B",
        artifact_type="C_FUNCTION",
        subsystem="ADAS",
        depth=1,
        path=["A", "B"],
        edge_relations=["SPECIFIED_BY"],
        confidence=0.9
    )

    trace = ProvenanceTracker.format_trace_chain(impact, g)
    assert "[Requirement] A (spec.json)" in trace
    assert "──[SPECIFIED_BY]──►" in trace
    assert "B (ctrl.c)" in trace

    mermaid = ProvenanceTracker.to_mermaid(impact)
    assert "graph LR" in mermaid
    assert "A -->|SPECIFIED_BY| B" in mermaid


def test_regression_selector_v2_safety_gate():
    g = EngineeringGraph()
    g.add_node(GraphNode(id="TEST_01", type=NodeType.TEST))
    g.add_node(GraphNode(id="TEST_SAFE_01", type=NodeType.TEST, safety_level=SafetyLevel.ASIL_D))

    t1 = TestRecord(
        test_id="TEST_01",
        description="Test 1",
        artifact_targets=["FUNC_01"],
        safety_class="QM",
        subsystem="ADAS",
        ecu="ECU_1",
        source_file="test_1.c"
    )
    mapper = TestMapper(all_tests=[t1], graph=g)

    safety_gate = SafetyGate()
    selector = RegressionSelector(g, mapper, safety_gate)

    selected = selector.select_tests(["FUNC_01"], ground_truth_safety_tests=["TEST_SAFE_01"], enforce_safety_gate=True)
    assert "TEST_01" in selected
    assert "TEST_SAFE_01" in selected

    eval_metrics = selector.evaluate_selection(selected, true_impacted_tests={"TEST_01"}, safety_critical_true_tests={"TEST_SAFE_01"})
    assert eval_metrics["safety_critical_recall"] == 1.0
    assert eval_metrics["false_negative_count"] == 0
