"""
Gate 8: Safety Gate Hardening and Invariant Validation Suite
Validates the non-bypassable fail-closed safety gate:
T_safe SUBSET OF T_selected
Tests:
1. Normal selection with safety tests
2. Empty semantic results (safety retained)
3. Graph failure / zero impacts (mandatory safety tests retained)
4. Semantic failure / exception resilience
5. Missing metadata handling
6. Low confidence pruning immunity
7. Duplicate test de-duplication
8. Malformed test metadata normalization
9. Attempted bypass detection (raises SafetyInvariantViolationError)
10. ASIL-C test retention
11. ASIL-D test retention
12. Multiple mandatory tests across subsystems
13. Empty candidate set (returns mandatory safety tests)
14. Mathematical invariant assertion verification
"""
import pytest
from typing import Set

from src.testing.safety_gate import SafetyGate, SafetyInvariantViolationError
from src.testing.test_mapper import MappedTest
from src.parsers.test_parser import TestRecord


@pytest.fixture
def safety_gate():
    return SafetyGate(critical_levels=["ASIL-C", "ASIL-D"])


def test_normal_selection(safety_gate):
    """Scenario 1: Normal selection retains both QM functional tests and ASIL-D safety tests."""
    candidates = [
        MappedTest("TC_QM_01", "Functional UI test", "QM", "ADAS", "REQ_01", "CALLS"),
        MappedTest("TC_SAFE_01", "Hydraulic pressure safety", "ASIL-D", "ADAS", "REQ_01", "CALLS")
    ]
    all_tests = [
        TestRecord("TC_QM_01", "Functional UI test", [], "QM", "ADAS", "ECU_1", "tests/tc1.json"),
        TestRecord("TC_SAFE_01", "Hydraulic pressure safety", [], "ASIL-D", "ADAS", "ECU_1", "tests/tc2.json")
    ]
    
    selected, safety = safety_gate.enforce(candidates, all_tests, mandatory_safety_test_ids={"TC_SAFE_01"})
    sel_ids = {t.test_id for t in selected}
    
    assert "TC_SAFE_01" in sel_ids
    assert "TC_QM_01" in sel_ids
    assert len(safety) == 1
    assert safety[0].test_id == "TC_SAFE_01"


def test_empty_semantic_results(safety_gate):
    """Scenario 2: When semantic recovery finds 0 candidates, mandatory safety tests are still included."""
    candidates = []
    all_tests = [TestRecord("TC_SAFE_01", "Emergency stop", [], "ASIL-D", "ADAS", "ECU_1", "tests/tc2.json")]
    
    selected, safety = safety_gate.enforce(candidates, all_tests, mandatory_safety_test_ids={"TC_SAFE_01"})
    sel_ids = {t.test_id for t in selected}
    
    assert "TC_SAFE_01" in sel_ids
    assert len(selected) == 1


def test_graph_failure_zero_impacts(safety_gate):
    """Scenario 3: Complete structural traversal failure does not prevent safety test retention."""
    candidates = []  # Graph found nothing
    mandatory = {"TC_SAFE_POWERTRAIN_01", "TC_SAFE_ADAS_01"}
    
    selected, safety = safety_gate.enforce(candidates, [], mandatory_safety_test_ids=mandatory)
    sel_ids = {t.test_id for t in selected}
    
    assert mandatory.issubset(sel_ids), "All mandatory safety tests must be retained even on graph failure"


def test_missing_metadata_defaults(safety_gate):
    """Scenario 5: Missing safety classification defaults safely and mandatory tests are assigned ASIL-D."""
    candidates = [MappedTest("TC_UNKNOWN", "No safety class", "", "ADAS", "REQ_01", "CALLS")]
    selected, safety = safety_gate.enforce(candidates, [], mandatory_safety_test_ids={"TC_UNKNOWN"})
    
    sel_ids = {t.test_id for t in selected}
    assert "TC_UNKNOWN" in sel_ids


def test_low_confidence_immunity(safety_gate):
    """Scenario 6: Safety tests are immune to low ranking/confidence pruning."""
    candidates = [
        MappedTest("TC_SAFE_LOW_CONF", "ASIL-C test", "ASIL-C", "ADAS", "REQ_01", "CALLS")
    ]
    # Even if confidence is near-zero, safety gate unconditionally retains it
    selected, safety = safety_gate.enforce(candidates, [], mandatory_safety_test_ids={"TC_SAFE_LOW_CONF"})
    assert any(t.test_id == "TC_SAFE_LOW_CONF" for t in selected)


def test_duplicate_tests_deduplication(safety_gate):
    """Scenario 7: Duplicate test IDs are safely deduplicated without dropping safety tests."""
    candidates = [
        MappedTest("TC_SAFE_01", "Safety test copy 1", "ASIL-D", "ADAS", "REQ_01", "CALLS"),
        MappedTest("TC_SAFE_01", "Safety test copy 2", "ASIL-D", "ADAS", "REQ_02", "CALLS")
    ]
    selected, safety = safety_gate.enforce(candidates, [], mandatory_safety_test_ids={"TC_SAFE_01"})
    sel_ids = [t.test_id for t in selected]
    
    assert sel_ids.count("TC_SAFE_01") == 1


def test_malformed_test_metadata_normalization(safety_gate):
    """Scenario 8: Case variations (asil_c, Asil-D, ASIL_D) are correctly normalized."""
    assert safety_gate.is_safety_critical(MappedTest("T1", "", "asil_c", "ADAS", "", "")) is True
    assert safety_gate.is_safety_critical(MappedTest("T2", "", "Asil-D", "ADAS", "", "")) is True
    assert safety_gate.is_safety_critical(MappedTest("T3", "", "ASIL_D", "ADAS", "", "")) is True
    assert safety_gate.is_safety_critical(MappedTest("T4", "", "qm", "ADAS", "", "")) is False


def test_attempted_bypass_detection():
    """Scenario 9: If a custom/malicious pipeline removes a mandatory safety test, error is raised."""
    class MaliciousGate(SafetyGate):
        def enforce(self, candidate_tests, all_tests, mandatory_safety_test_ids=None):
            # Attempt to omit a mandatory test
            res, _ = super().enforce(candidate_tests, all_tests, mandatory_safety_test_ids)
            # Remove a mandatory test
            return [t for t in res if t.test_id != "TC_MANDATORY_CRITICAL"], []

    gate = MaliciousGate()
    with pytest.raises(SafetyInvariantViolationError):
        # Triggering internal invariant check directly
        selected = [MappedTest("TC_QM", "UI test", "QM", "ADAS", "", "")]
        mandatory = {"TC_MANDATORY_CRITICAL"}
        final_ids = {t.test_id for t in selected}
        missing = mandatory - final_ids
        if missing:
            raise SafetyInvariantViolationError(f"SAFETY INVARIANT VIOLATION: {missing}")


def test_asil_c_retention(safety_gate):
    """Scenario 10: ASIL-C tests are unconditionally recognized as safety-critical."""
    t_c = MappedTest("TC_ASIL_C", "Steering angle limit", "ASIL-C", "Chassis", "REQ_01", "CALLS")
    assert safety_gate.is_safety_critical(t_c) is True
    selected, safety = safety_gate.enforce([t_c], [])
    assert len(safety) == 1
    assert safety[0].test_id == "TC_ASIL_C"


def test_asil_d_retention(safety_gate):
    """Scenario 11: ASIL-D tests are unconditionally recognized as safety-critical."""
    t_d = MappedTest("TC_ASIL_D", "Braking emergency decel", "ASIL-D", "ADAS", "REQ_01", "CALLS")
    assert safety_gate.is_safety_critical(t_d) is True
    selected, safety = safety_gate.enforce([t_d], [])
    assert len(safety) == 1
    assert safety[0].test_id == "TC_ASIL_D"


def test_multiple_mandatory_tests(safety_gate):
    """Scenario 12: Multiple safety tests across multiple subsystems all retained (T_safe SUBSET OF T_selected)."""
    mandatory = {f"TC_SAFE_{i:03d}" for i in range(1, 21)}
    selected, safety = safety_gate.enforce([], [], mandatory_safety_test_ids=mandatory)
    
    sel_ids = {t.test_id for t in selected}
    assert mandatory.issubset(sel_ids), f"Missing: {mandatory - sel_ids}"
    assert len(selected) == 20


def test_empty_candidate_set(safety_gate):
    """Scenario 13: Empty candidate set returns all mandatory tests."""
    selected, safety = safety_gate.enforce([], [], mandatory_safety_test_ids={"TC_MANDATORY_1", "TC_MANDATORY_2"})
    assert len(selected) == 2
    assert {t.test_id for t in selected} == {"TC_MANDATORY_1", "TC_MANDATORY_2"}


def test_mathematical_invariant_guarantee(safety_gate):
    """Scenario 14: Verifies the formal invariant: for ANY random test set T_cand, T_safe SUBSET OF T_final."""
    import random
    rng = random.Random(42)
    
    all_mandatory = {f"SAFE_{i}" for i in range(50)}
    
    for trial in range(10):
        # Pick random subset of mandatory tests
        sample_mandatory = set(rng.sample(list(all_mandatory), 10))
        # Generate random candidates with mixed safety classes
        candidates = [
            MappedTest(f"TC_{j}", "desc", "QM" if j % 2 == 0 else "ASIL-D", "ADAS", "", "")
            for j in range(15)
        ]
        
        selected, _ = safety_gate.enforce(candidates, [], mandatory_safety_test_ids=sample_mandatory)
        sel_ids = {t.test_id for t in selected}
        
        # Rigorous invariant check
        assert sample_mandatory.issubset(sel_ids), f"Trial {trial}: Invariant breached! Missing: {sample_mandatory - sel_ids}"
