"""
Unit Tests for Safety Gate and Invariant Retention
"""
import pytest
from src.testing.safety_gate import SafetyGate, SafetyInvariantViolationError
from src.testing.test_mapper import MappedTest
from src.parsers.test_parser import TestRecord


def test_safety_gate_retains_asil_d_tests():
    gate = SafetyGate(critical_levels=["ASIL-C", "ASIL-D"])
    
    t_qm = MappedTest("TC_QM", "QM Test", "QM", "ADAS", "ART_1", "EXPLICIT")
    t_d = MappedTest("TC_D", "ASIL-D Safety Test", "ASIL-D", "ADAS", "ART_2", "EXPLICIT")
    
    all_records = [
        TestRecord("TC_QM", "QM Test", ["ART_1"], "QM", "ADAS", "ECU_1", "f.json"),
        TestRecord("TC_D", "ASIL-D Safety Test", ["ART_2"], "ASIL-D", "ADAS", "ECU_1", "f.json")
    ]

    selected, retained_safety = gate.enforce(
        candidate_tests=[t_qm, t_d],
        all_tests=all_records,
        mandatory_safety_test_ids={"TC_D"}
    )

    sel_ids = [t.test_id for t in selected]
    assert "TC_D" in sel_ids
    assert len(retained_safety) == 1
    assert retained_safety[0].test_id == "TC_D"


def test_safety_gate_cannot_be_bypassed():
    gate = SafetyGate(critical_levels=["ASIL-C", "ASIL-D"])
    all_records = [
        TestRecord("TC_SAFE_01", "Critical brake test", ["ART_SAFE"], "ASIL-D", "ADAS", "ECU_1", "f.json")
    ]

    # Mandatory test missing from candidate list must be automatically retained or raise error if violated
    selected, retained_safety = gate.enforce(
        candidate_tests=[],
        all_tests=all_records,
        mandatory_safety_test_ids={"TC_SAFE_01"}
    )
    assert "TC_SAFE_01" in [t.test_id for t in selected]
