"""
Adversarial & Stress Tests for AURA-Impact Prototype
"""
import pytest
from pathlib import Path
from src.api.pipeline import AuraImpactPipeline
from src.ingestion.git_diff import ChangedArtifact
from src.graph.builder import EngineeringGraph
from src.graph.schema import GraphNode, GraphEdge, NodeType, RelationType
from src.graph.traversal import BoundedGraphTraverser


def test_cyclic_graph_termination():
    graph = EngineeringGraph("CYCLIC_TEST")
    graph.add_node(GraphNode("FN_A", NodeType.C_FUNCTION, "Fn A", "ADAS", "ECU_1"))
    graph.add_node(GraphNode("FN_B", NodeType.C_FUNCTION, "Fn B", "ADAS", "ECU_1"))
    graph.add_node(GraphNode("FN_C", NodeType.C_FUNCTION, "Fn C", "ADAS", "ECU_1"))

    graph.add_edge(GraphEdge("FN_A", "FN_B", RelationType.CALLS))
    graph.add_edge(GraphEdge("FN_B", "FN_C", RelationType.CALLS))
    graph.add_edge(GraphEdge("FN_C", "FN_A", RelationType.CALLS))  # Cycle

    traverser = BoundedGraphTraverser(graph, max_depth=5)
    impacts = traverser.get_explicit_impacts(["FN_A"])
    # Visited set must prevent infinite loops
    assert len(impacts) == 2
    assert set([imp.artifact_id for imp in impacts]) == {"FN_B", "FN_C"}


def test_decoy_distractor_suppression():
    pipeline = AuraImpactPipeline()
    pipeline.ingest_repository(Path("examples/demo_repo"))

    # Decoy change query in Body Electronics referencing brake keywords
    decoy_change = ChangedArtifact(
        artifact_id="REQ_BODY_DECOY",
        artifact_type="Requirement",
        subsystem="Body_Electronics",
        ecu="ECU_Body",
        change_type="MODIFY",
        change_semantics="Brake pedal lamp illumination circuit test"
    )

    imp_res, test_res, rep = pipeline.analyze_change(decoy_change)
    # ADAS brake function must NOT be retrieved due to subsystem isolation
    retrieved_ids = [imp.artifact_id for imp in imp_res.final_impacts]
    assert "C_Function_TriggerBrake" not in retrieved_ids


def test_ambiguous_requirement_routing():
    pipeline = AuraImpactPipeline()
    pipeline.ingest_repository(Path("examples/demo_repo"))

    amb_change = ChangedArtifact(
        artifact_id="REQ_AMB_TEST",
        artifact_type="Requirement",
        subsystem="ADAS",
        ecu="ECU_1",
        change_type="MODIFY",
        change_semantics="Ambiguous alert logic without clear threshold"
    )

    imp_res, test_res, rep = pipeline.analyze_change(amb_change)
    assert len(imp_res.review_required_items) > 0
