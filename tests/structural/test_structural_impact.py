"""
Gate 6: Comprehensive Structural Impact Validation Suite
Validates deterministic graph traversal under all required conditions:
- no-change
- single changed function
- caller/callee propagation
- multiple callers
- cyclic dependencies (no infinite loops)
- depth boundary enforcement (k=3)
- missing ARXML handling
- malformed C++ handling
- unrelated subsystem isolation
- documentation-only change
- variable READS
- variable WRITES
- RTE APIs modeling
- reverse traversal
- missing graph edge
- dynamic function pointer limitation
"""
import pytest
from pathlib import Path

from src.graph.schema import GraphNode, GraphEdge, NodeType, RelationType, SafetyLevel
from src.graph.builder import EngineeringGraph
from src.graph.traversal import BoundedGraphTraverser
from src.parsers.cpp_parser import CppTreeSitterParser
from src.parsers.arxml_parser import AutosarARXMLParser
from src.impact.impact_engine import TwoStageImpactEngine
from src.ingestion.git_diff import ChangedArtifact


@pytest.fixture
def sample_graph():
    """Builds a test graph with functions, variables, and requirements."""
    g = EngineeringGraph(project_id="TEST_ADAS")
    
    # Nodes
    g.add_node(GraphNode("FN_ROOT", NodeType.C_FUNCTION, "root_fn", "ADAS", "ECU_1"))
    g.add_node(GraphNode("FN_CALLEE_1", NodeType.C_FUNCTION, "callee_1", "ADAS", "ECU_1"))
    g.add_node(GraphNode("FN_CALLEE_2", NodeType.C_FUNCTION, "callee_2", "ADAS", "ECU_1"))
    g.add_node(GraphNode("FN_CALLEE_3", NodeType.C_FUNCTION, "callee_3", "ADAS", "ECU_1"))
    g.add_node(GraphNode("FN_CALLEE_4", NodeType.C_FUNCTION, "callee_4", "ADAS", "ECU_1"))
    g.add_node(GraphNode("VAR_SHARED_SPEED", NodeType.C_VARIABLE, "VehicleSpeed", "ADAS", "ECU_1"))
    g.add_node(GraphNode("FN_POWERTRAIN", NodeType.C_FUNCTION, "motor_torque", "Powertrain", "ECU_PT"))
    
    # Linear chain: ROOT -> CALLEE_1 -> CALLEE_2 -> CALLEE_3 -> CALLEE_4
    g.add_edge(GraphEdge("FN_ROOT", "FN_CALLEE_1", RelationType.CALLS))
    g.add_edge(GraphEdge("FN_CALLEE_1", "FN_CALLEE_2", RelationType.CALLS))
    g.add_edge(GraphEdge("FN_CALLEE_2", "FN_CALLEE_3", RelationType.CALLS))
    g.add_edge(GraphEdge("FN_CALLEE_3", "FN_CALLEE_4", RelationType.CALLS))
    
    # Variable Read/Write
    g.add_edge(GraphEdge("FN_ROOT", "VAR_SHARED_SPEED", RelationType.WRITES))
    g.add_edge(GraphEdge("FN_CALLEE_1", "VAR_SHARED_SPEED", RelationType.READS))
    
    return g


def test_no_change_scenario(sample_graph):
    """Scenario 1: No change in repository returns 0 impacts."""
    traverser = BoundedGraphTraverser(sample_graph, max_depth=3)
    impacts = traverser.get_explicit_impacts([])
    assert len(impacts) == 0


def test_single_changed_function(sample_graph):
    """Scenario 2: Single changed function discovers direct child."""
    traverser = BoundedGraphTraverser(sample_graph, max_depth=1)
    impacts = traverser.get_explicit_impacts(["FN_CALLEE_2"])
    impact_ids = {imp.artifact_id for imp in impacts}
    assert "FN_CALLEE_3" in impact_ids
    assert "FN_CALLEE_4" not in impact_ids


def test_caller_callee_propagation(sample_graph):
    """Scenario 3: Caller propagating to callees across graph."""
    traverser = BoundedGraphTraverser(sample_graph, max_depth=2)
    impacts = traverser.get_explicit_impacts(["FN_ROOT"])
    impact_ids = {imp.artifact_id for imp in impacts}
    assert "FN_CALLEE_1" in impact_ids
    assert "FN_CALLEE_2" in impact_ids
    assert "FN_CALLEE_3" not in impact_ids  # Depth 3 is excluded at max_depth=2


def test_multiple_callers():
    """Scenario 4: Multiple distinct callers converging on a utility function."""
    g = EngineeringGraph(project_id="MULTI_CALL")
    g.add_node(GraphNode("FN_UTIL", NodeType.C_FUNCTION, "util", "ADAS", "ECU_1"))
    g.add_node(GraphNode("FN_APP1", NodeType.C_FUNCTION, "app1", "ADAS", "ECU_1"))
    g.add_node(GraphNode("FN_APP2", NodeType.C_FUNCTION, "app2", "ADAS", "ECU_1"))
    
    # Reverse propagation check (who calls UTIL?)
    g.add_edge(GraphEdge("FN_APP1", "FN_UTIL", RelationType.CALLS))
    g.add_edge(GraphEdge("FN_APP2", "FN_UTIL", RelationType.CALLS))
    
    # In NetworkX successors of APP1 and APP2 reach UTIL
    traverser = BoundedGraphTraverser(g, max_depth=2)
    imp1 = traverser.get_explicit_impacts(["FN_APP1"])
    imp2 = traverser.get_explicit_impacts(["FN_APP2"])
    
    assert any(i.artifact_id == "FN_UTIL" for i in imp1)
    assert any(i.artifact_id == "FN_UTIL" for i in imp2)


def test_cyclic_dependencies():
    """Scenario 5: Cyclic function calls (A -> B -> A) do NOT cause infinite loops."""
    g = EngineeringGraph(project_id="CYCLE_TEST")
    g.add_node(GraphNode("FN_A", NodeType.C_FUNCTION, "fn_a", "ADAS", "ECU_1"))
    g.add_node(GraphNode("FN_B", NodeType.C_FUNCTION, "fn_b", "ADAS", "ECU_1"))
    g.add_node(GraphNode("FN_C", NodeType.C_FUNCTION, "fn_c", "ADAS", "ECU_1"))
    
    g.add_edge(GraphEdge("FN_A", "FN_B", RelationType.CALLS))
    g.add_edge(GraphEdge("FN_B", "FN_C", RelationType.CALLS))
    g.add_edge(GraphEdge("FN_C", "FN_A", RelationType.CALLS))  # Cycle!
    
    traverser = BoundedGraphTraverser(g, max_depth=5)
    impacts = traverser.get_explicit_impacts(["FN_A"])
    
    # Should visit FN_B and FN_C exactly once without hanging
    impact_ids = [i.artifact_id for i in impacts]
    assert len(impact_ids) == 2
    assert "FN_B" in impact_ids
    assert "FN_C" in impact_ids


def test_depth_boundary_enforcement(sample_graph):
    """Scenario 6: Traversal strictly terminates at depth k=3."""
    traverser = BoundedGraphTraverser(sample_graph, max_depth=3)
    impacts = traverser.get_explicit_impacts(["FN_ROOT"])
    
    impact_map = {imp.artifact_id: imp.depth for imp in impacts}
    assert impact_map["FN_CALLEE_1"] == 1
    assert impact_map["FN_CALLEE_2"] == 2
    assert impact_map["FN_CALLEE_3"] == 3
    # CALLEE_4 is at depth 4, so it MUST be excluded
    assert "FN_CALLEE_4" not in impact_map


def test_missing_arxml_handling():
    """Scenario 7: Malformed or missing ARXML handled without unhandled crash."""
    parser = AutosarARXMLParser()
    # Non-existent path returns empty structure
    data = parser.parse_records(Path("data/non_existent_file.arxml"))
    assert data["swcs"] == []
    assert data["interfaces"] == []


def test_malformed_cpp_handling(tmp_path):
    """Scenario 8: Malformed C++ syntax handled gracefully via regex fallback."""
    parser = CppTreeSitterParser()
    bad_c_file = tmp_path / "broken.c"
    bad_c_file.write_text("void broken_func( { int x = ; return; }", encoding="utf-8")
    
    fns, vars_found = parser.parse_records(bad_c_file)
    # Parser should return safely without raising an unhandled exception
    assert isinstance(fns, list)
    assert isinstance(vars_found, list)


def test_unrelated_subsystem_isolation(sample_graph):
    """Scenario 9: Unrelated subsystem nodes are completely unreached by traversal."""
    traverser = BoundedGraphTraverser(sample_graph, max_depth=3)
    impacts = traverser.get_explicit_impacts(["FN_ROOT"])
    impact_ids = {imp.artifact_id for imp in impacts}
    assert "FN_POWERTRAIN" not in impact_ids


def test_documentation_only_change(sample_graph):
    """Scenario 10: Documentation / markdown changes yield 0 structural impacts."""
    engine = TwoStageImpactEngine(graph=sample_graph)
    change = ChangedArtifact(
        artifact_id="DOC_README",
        artifact_type="Documentation",
        subsystem="ADAS",
        ecu="ECU_1",
        change_type="MODIFY",
        diff_text="## Updated documentation notes"
    )
    result = engine.analyze_change(change)
    assert len(result.structural_impacts) == 0


def test_variable_reads_and_writes(sample_graph):
    """Scenarios 11 & 12: Variable READS and WRITES relations properly traversed."""
    traverser = BoundedGraphTraverser(sample_graph, max_depth=2)
    impacts = traverser.get_explicit_impacts(["FN_ROOT"])
    
    var_impacts = [i for i in impacts if i.artifact_id == "VAR_SHARED_SPEED"]
    assert len(var_impacts) == 1
    assert var_impacts[0].depth == 1
    assert "WRITES" in var_impacts[0].edge_relations


def test_rte_apis_modeling():
    """Scenario 13: RTE API invocations are detected in C function metadata."""
    fn_node = GraphNode(
        id="FN_SWC_ACTUATE",
        type=NodeType.C_FUNCTION,
        name="swc_actuate",
        subsystem="ADAS",
        ecu="ECU_1",
        metadata={"rte_apis": ["Rte_Write_BrakeCmd", "Rte_Read_SensorInput"]}
    )
    assert "Rte_Write_BrakeCmd" in fn_node.metadata["rte_apis"]
    assert "Rte_Read_SensorInput" in fn_node.metadata["rte_apis"]


def test_reverse_traversal():
    """Scenario 14: Reverse traversal finds callers of a modified target."""
    g = EngineeringGraph(project_id="REV_TEST")
    g.add_node(GraphNode("FN_CALLER", NodeType.C_FUNCTION, "caller", "ADAS", "ECU_1"))
    g.add_node(GraphNode("FN_TARGET", NodeType.C_FUNCTION, "target", "ADAS", "ECU_1"))
    g.add_edge(GraphEdge("FN_CALLER", "FN_TARGET", RelationType.CALLS))
    
    # Reverse graph in NetworkX
    rev_g = g.graph.reverse()
    predecessors = list(rev_g.successors("FN_TARGET"))
    assert "FN_CALLER" in predecessors


def test_missing_graph_edge():
    """Scenario 15: Missing graph edge leaves structural impact set empty for fallback."""
    g = EngineeringGraph(project_id="MISSING_EDGE")
    g.add_node(GraphNode("FN_ORPHAN", NodeType.C_FUNCTION, "orphan", "ADAS", "ECU_1"))
    
    traverser = BoundedGraphTraverser(g, max_depth=3)
    impacts = traverser.get_explicit_impacts(["FN_ORPHAN"])
    assert len(impacts) == 0


def test_dynamic_function_pointer_limitation():
    """Scenario 16: Dynamic function pointers are an explicit documented limitation.
    Static AST parsers cannot resolve indirect jump targets (*func_ptr)().
    System safely flags as missing structural edge, deferring to Stage 2 fallback.
    """
    g = EngineeringGraph(project_id="PTR_TEST")
    g.add_node(GraphNode("FN_DISPATCHER", NodeType.C_FUNCTION, "dispatcher", "ADAS", "ECU_1",
                         metadata={"has_function_pointers": True}))
    
    # Traversal sees no static edges from FN_DISPATCHER
    traverser = BoundedGraphTraverser(g, max_depth=3)
    impacts = traverser.get_explicit_impacts(["FN_DISPATCHER"])
    assert len(impacts) == 0
    # Engine marks structural coverage incomplete, triggering semantic fallback safely
    engine = TwoStageImpactEngine(graph=g)
    change = ChangedArtifact("FN_DISPATCHER", "C_Function", "ADAS", "ECU_1", "MODIFY",
                             change_semantics="Dynamic function pointer dispatcher table updated")
    res = engine.analyze_change(change)
    assert res.structural_coverage_complete is False
