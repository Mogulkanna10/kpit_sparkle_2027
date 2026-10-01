"""
Unit tests for engineering graph and traversal
"""
import pytest
from src.graph.schema import Node, Edge, NodeType, EdgeType, SafetyLevel
from src.graph.builder import EngineeringGraph
from src.graph.traversal import GraphTraverser


def test_engineering_graph_creation():
    g = EngineeringGraph("TestGraph")
    n1 = Node(id="R1", type=NodeType.REQUIREMENT, name="Req 1", file_path="r.json", project="Test")
    n2 = Node(id="SWC1", type=NodeType.SWC, name="SWC 1", file_path="s.arxml", project="Test")
    n3 = Node(id="FN1", type=NodeType.C_FUNCTION, name="Func 1", file_path="f.c", project="Test")

    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)

    e1 = Edge(source_id="R1", target_id="SWC1", relation=EdgeType.IMPLEMENTS, source_file="r.json")
    e2 = Edge(source_id="SWC1", target_id="FN1", relation=EdgeType.CALLS, source_file="s.arxml")

    g.add_edge(e1)
    g.add_edge(e2)

    assert g.graph.number_of_nodes() == 3
    assert g.graph.number_of_edges() == 2

    traverser = GraphTraverser(g, max_depth=5)
    impact = traverser.propagate_downstream(["R1"])

    assert "R1" in impact
    assert "SWC1" in impact
    assert "FN1" in impact
    assert impact["FN1"]["distance"] == 2
    assert impact["FN1"]["structural_score"] < 1.0
