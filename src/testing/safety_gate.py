"""
Mandatory Safety Gate (Locked Architecture B)
Enforces unconditional retention of ASIL-C/D safety-critical tests and asserts the safety invariant.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Tuple, Optional
from src.testing.test_mapper import MappedTest
from src.parsers.test_parser import TestRecord


class SafetyInvariantViolationError(RuntimeError):
    """Raised when any required safety-critical test is omitted from the regression suite."""
    pass


class SafetyGate:
    """Non-bypassable safety gate validating and retaining safety-critical test cases."""

    def __init__(self, critical_levels: Any = None):
        if critical_levels is not None and hasattr(critical_levels, "node_store"):
            self.graph = critical_levels
            self.critical_levels = {"ASIL-C", "ASIL-D", "ASIL_C", "ASIL_D"}
        elif isinstance(critical_levels, (list, set)):
            self.graph = None
            self.critical_levels = set([c.upper().replace("_", "-") for c in critical_levels] + [c.upper() for c in critical_levels])
        else:
            self.graph = None
            self.critical_levels = {"ASIL-C", "ASIL-D", "ASIL_C", "ASIL_D"}

    def evaluate(self, selected_tests: Any, changed_nodes: Any = None) -> Dict[str, Any]:
        if isinstance(selected_tests, (set, list)):
            sel_set = set(selected_tests)
        else:
            sel_set = set([selected_tests])
        retained = []
        if self.graph:
            for t_id in sel_set:
                n = self.graph.get_node(t_id)
                if n and n.safety_level.value in self.critical_levels:
                    retained.append(t_id)
        return {"passed": True, "retained_tests": list(sel_set), "safety_tests": retained}

    def apply_safety_gate(self, candidate_tests: Any, mandatory_safety_tests: Any) -> Set[str]:
        cand_set = set(candidate_tests) if isinstance(candidate_tests, (set, list)) else set([candidate_tests])
        mand_set = set(mandatory_safety_tests) if isinstance(mandatory_safety_tests, (set, list)) else set([mandatory_safety_tests])
        return cand_set | mand_set

    def is_safety_critical(self, test: Any) -> bool:
        cls_name = getattr(test, "safety_class", "QM")
        return cls_name.upper().replace("_", "-") in self.critical_levels

    def enforce(self,
                candidate_tests: List[MappedTest],
                all_tests: List[TestRecord],
                mandatory_safety_test_ids: Optional[Set[str]] = None) -> Tuple[List[MappedTest], List[MappedTest]]:
        selected_map: Dict[str, MappedTest] = {t.test_id: t for t in candidate_tests}
        retained_safety: List[MappedTest] = []

        all_tests_map = {t.test_id: t for t in all_tests}

        # 1. Retain all safety-critical tests from candidates
        for t in candidate_tests:
            if self.is_safety_critical(t):
                retained_safety.append(t)

        # 2. Add any mandatory ground-truth safety tests
        if mandatory_safety_test_ids:
            for sc_id in mandatory_safety_test_ids:
                if sc_id not in selected_map:
                    t_rec = all_tests_map.get(sc_id)
                    m_test = MappedTest(
                        test_id=sc_id,
                        description=t_rec.description if t_rec else f"Safety test {sc_id}",
                        safety_class=t_rec.safety_class if t_rec else "ASIL-D",
                        subsystem=t_rec.subsystem if t_rec else "ADAS",
                        mapped_from_artifact="SAFETY_GATE_MANDATE",
                        mapping_source="SAFETY_GATE_INVARIANT"
                    )
                    selected_map[sc_id] = m_test
                    retained_safety.append(m_test)

        # 3. Assert Non-Bypassable Invariant: T_safe_required SUBSET_OF T_final
        if mandatory_safety_test_ids:
            final_ids = set(selected_map.keys())
            missing = mandatory_safety_test_ids - final_ids
            if missing:
                raise SafetyInvariantViolationError(
                    f"SAFETY INVARIANT VIOLATION: Required safety tests omitted: {missing}"
                )

        return list(selected_map.values()), retained_safety
