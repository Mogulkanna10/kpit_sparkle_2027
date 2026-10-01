"""
Deterministic Test Mapper
Maps impacted engineering artifacts to verification test suites.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Optional

from src.impact.impact_union import Impact
from src.graph.builder import EngineeringGraph
from src.parsers.test_parser import TestRecord


@dataclass
class MappedTest:
    test_id: str
    description: str
    safety_class: str  # QM, ASIL_A, ASIL_B, ASIL_C, ASIL_D
    subsystem: str
    mapped_from_artifact: str
    mapping_source: str  # EXPLICIT_TRACE, STRUCTURAL_GRAPH, SEMANTIC_RECOVERY
    source_file: str = ""


class TestMapper:
    """Finds all verification test cases exercising impacted artifacts."""
    __test__ = False

    def __init__(self, all_tests: Any = None, graph: Optional[EngineeringGraph] = None):
        self.all_tests: Dict[str, Any] = {}
        self.target_to_tests: Dict[str, List[Any]] = {}

        if all_tests is not None and hasattr(all_tests, "node_store"):
            self.graph = all_tests
            # Graph passed as first argument
            for nid, n in all_tests.node_store.items():
                if "test" in (n.type.value if hasattr(n.type, "value") else str(n.type)).lower():
                    self.all_tests[nid] = n
        elif isinstance(all_tests, list):
            self.graph = graph
            for t in all_tests:
                self.all_tests[t.test_id] = t
                for tgt in getattr(t, "artifact_targets", []):
                    self.target_to_tests.setdefault(tgt, []).append(t)
        else:
            self.graph = graph

    def map_impacted_artifacts(self, impacted_ids: Any) -> Set[str]:
        if isinstance(impacted_ids, str):
            impacted_ids = [impacted_ids]
        matched = set()
        for i_id in impacted_ids:
            if i_id in self.target_to_tests:
                for t in self.target_to_tests[i_id]:
                    matched.add(t.test_id)
            if self.graph and self.graph.has_node(i_id):
                for nbr in self.graph.get_neighbors(i_id, direction="both"):
                    node = self.graph.get_node(nbr)
                    if node and "test" in (node.type.value if hasattr(node.type, "value") else str(node.type)).lower():
                        matched.add(nbr)
        return matched

    map_impacted_artifacts_to_tests = map_impacted_artifacts

    def map_impacts_to_tests(self, impacts: List[Impact]) -> List[MappedTest]:
        mapped: Dict[str, MappedTest] = {}

        for imp in impacts:
            art_id = imp.artifact_id

            # 1. Direct explicit test target mapping
            if art_id in self.target_to_tests:
                for t in self.target_to_tests[art_id]:
                    if t.test_id not in mapped:
                        mapped[t.test_id] = MappedTest(
                            test_id=t.test_id,
                            description=t.description,
                            safety_class=t.safety_class,
                            subsystem=t.subsystem,
                            mapped_from_artifact=art_id,
                            mapping_source="EXPLICIT_TRACE",
                            source_file=t.source_file
                        )

            # 2. Graph neighbor test mapping
            if self.graph and self.graph.has_node(art_id):
                for nbr in self.graph.get_neighbors(art_id, direction="both"):
                    node = self.graph.get_node(nbr)
                    if node and "test" in (node.type.value if hasattr(node.type, "value") else str(node.type)).lower():
                        if nbr not in mapped:
                            t_rec = self.all_tests.get(nbr)
                            mapped[nbr] = MappedTest(
                                test_id=nbr,
                                description=getattr(t_rec, "description", node.name) if t_rec else node.name,
                                safety_class=getattr(t_rec, "safety_class", node.safety_level.value if hasattr(node.safety_level, "value") else str(node.safety_level)) if t_rec else (node.safety_level.value if hasattr(node.safety_level, "value") else str(node.safety_level)),
                                subsystem=node.subsystem,
                                mapped_from_artifact=art_id,
                                mapping_source="STRUCTURAL_GRAPH",
                                source_file=node.source_file
                            )

        return list(mapped.values())
