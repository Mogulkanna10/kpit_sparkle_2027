"""
Unit Tests for Engineering Graph and Bounded Traversal
"""
import pytest
from src.graph.builder import EngineeringGraph
from src.graph.schema import GraphNode, GraphEdge, NodeType, RelationType, SafetyLevel
from src.graph.traversal import BoundedGraphTraverser
from src.graph.provenance import ProvenanceTracker


def test_graph_construction_and_traversal():
    graph = EngineeringGraph("TEST_PROJECT")

    n1 = GraphNode("REQ_01", NodeType.REQUIREMENT, "Req 01", "ADAS", "ECU_1")
    n2 = GraphNode("SWC_01", NodeType.SWC, "SWC 01", "ADAS", "ECU_1")
    n3 = GraphNode("FN_01", NodeType.C_FUNCTION, "Fn 01", "ADAS", "ECU_1")

    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    graph.add_edge(GraphEdge("REQ_01", "SWC_01", RelationType.MAPS_TO))
    graph.add_edge(GraphEdge("SWC_01", "FN_01", RelationType.OWNS))

    traverser = BoundedGraphTraverser(graph, max_depth=3)
    impacts = traverser.get_explicit_impacts(["REQ_01"])

    impact_ids = [imp.artifact_id for imp in impacts]
    assert "SWC_01" in impact_ids
    assert "FN_01" in impact_ids
    assert len(impacts) == 2

    # Check Provenance formatting
    chain = ProvenanceTracker.format_trace_chain(impacts[1], graph)
    assert "REQ_01" in chain
    assert "FN_01" in chain


def test_depth_bounding():
    graph = EngineeringGraph("DEPTH_TEST")
    for i in range(10):
        graph.add_node(GraphNode(f"N_{i}", NodeType.C_FUNCTION, f"Node {i}", "ADAS", "ECU_1"))
        if i > 0:
            graph.add_edge(GraphEdge(f"N_{i-1}", f"N_{i}", RelationType.CALLS))

    traverser = BoundedGraphTraverser(graph, max_depth=2)
    impacts = traverser.get_explicit_impacts(["N_0"])
    assert len(impacts) == 2
    assert [imp.artifact_id for imp in impacts] == ["N_1", "N_2"]
