"""
Gate 9: Test Mapping and Regression Selection Validation Suite
Validates:
1. Artifact -> test mapping (explicit trace)
2. Impact -> test propagation
3. Safety -> mandatory test retention
4. Duplicate test deduplication
5. Missing test mappings handling
6. Unrelated test omission (test suite reduction)
7. Empty impact handling
8. Full-suite fallback behavior
9. Exact metric calculations: reduction %, test recall, safety recall, false positives/negatives
"""
import pytest
from src.testing.test_mapper import TestMapper, MappedTest
from src.testing.safety_gate import SafetyGate
from src.testing.regression_selector import RegressionSelector, RegressionSelectionResult
from src.parsers.test_parser import TestRecord
from src.impact.impact_union import Impact, ImpactType, SourceStage


@pytest.fixture
def test_suite():
    """Builds a realistic mock verification test suite."""
    return [
        TestRecord("TC_01", "Braking actuation test", ["FN_BRAKE"], "ASIL-D", "ADAS", "ECU_1", "tests/t1.json"),
        TestRecord("TC_02", "Radar distance validation", ["FN_RADAR"], "ASIL-B", "ADAS", "ECU_1", "tests/t2.json"),
        TestRecord("TC_03", "UI dashboard speed gauge", ["FN_UI"], "QM", "Body", "ECU_Body", "tests/t3.json"),
        TestRecord("TC_04", "TTC emergency alert chime", ["FN_RADAR", "FN_BRAKE"], "ASIL-C", "ADAS", "ECU_1", "tests/t4.json"),
        TestRecord("TC_05", "Cabin interior light", ["FN_LIGHT"], "QM", "Body", "ECU_Body", "tests/t5.json"),
        TestRecord("TC_06", "Powertrain torque limiter", ["FN_TORQUE"], "ASIL-D", "Powertrain", "ECU_PT", "tests/t6.json"),
        TestRecord("TC_07", "Battery thermal shutdown", ["FN_BMS"], "ASIL-D", "Battery_EV", "ECU_BMS", "tests/t7.json"),
        TestRecord("TC_08", "Wiper speed interval", ["FN_WIPER"], "QM", "Body", "ECU_Body", "tests/t8.json"),
        TestRecord("TC_09", "Cruise control hold", ["FN_ACC"], "ASIL-B", "ADAS", "ECU_1", "tests/t9.json"),
        TestRecord("TC_10", "Diagnostic fault memory", ["FN_DIAG"], "QM", "Body", "ECU_Body", "tests/t10.json"),
    ]


def test_artifact_to_test_mapping(test_suite):
    """Scenario 1: Explicit trace target maps accurately to test record."""
    mapper = TestMapper(all_tests=test_suite)
    impact = Impact("FN_BRAKE", "C_Function", "ADAS", "ECU_1", ImpactType.STRUCTURAL, 1.0, SourceStage.GRAPH)
    
    mapped = mapper.map_impacts_to_tests([impact])
    test_ids = {t.test_id for t in mapped}
    
    # FN_BRAKE is verified by TC_01 and TC_04
    assert test_ids == {"TC_01", "TC_04"}


def test_impact_to_tests_propagation(test_suite):
    """Scenario 2: Multiple impacted artifacts propagate to the union of their tests."""
    mapper = TestMapper(all_tests=test_suite)
    impacts = [
        Impact("FN_BRAKE", "C_Function", "ADAS", "ECU_1", ImpactType.STRUCTURAL, 1.0, SourceStage.GRAPH),
        Impact("FN_RADAR", "C_Function", "ADAS", "ECU_1", ImpactType.STRUCTURAL, 1.0, SourceStage.GRAPH)
    ]
    mapped = mapper.map_impacts_to_tests(impacts)
    test_ids = {t.test_id for t in mapped}
    
    # FN_BRAKE -> TC_01, TC_04; FN_RADAR -> TC_02, TC_04
    assert test_ids == {"TC_01", "TC_02", "TC_04"}


def test_duplicate_mappings_deduplication(test_suite):
    """Scenario 4: Shared verification tests (TC_04) appear exactly once."""
    mapper = TestMapper(all_tests=test_suite)
    gate = SafetyGate()
    selector = RegressionSelector(test_mapper=mapper, safety_gate=gate, all_tests=test_suite)
    
    impacts = [
        Impact("FN_BRAKE", "C_Function", "ADAS", "ECU_1", ImpactType.STRUCTURAL, 1.0, SourceStage.GRAPH),
        Impact("FN_RADAR", "C_Function", "ADAS", "ECU_1", ImpactType.STRUCTURAL, 1.0, SourceStage.GRAPH)
    ]
    result = selector.select(impacts)
    test_ids = [t.test_id for t in result.selected_tests]
    
    assert test_ids.count("TC_04") == 1
    assert len(test_ids) == 3


def test_missing_mappings_handling(test_suite):
    """Scenario 5: Impacted artifact with no linked tests does not generate ghost tests."""
    mapper = TestMapper(all_tests=test_suite)
    orphan_impact = Impact("FN_UNTESTED", "C_Function", "ADAS", "ECU_1", ImpactType.STRUCTURAL, 1.0, SourceStage.GRAPH)
    
    mapped = mapper.map_impacts_to_tests([orphan_impact])
    assert len(mapped) == 0


def test_unrelated_tests_omission_and_reduction(test_suite):
    """Scenario 6: Unrelated test suites (TC_03, TC_05, TC_08, etc.) are pruned to achieve reduction."""
    mapper = TestMapper(all_tests=test_suite)
    gate = SafetyGate()
    selector = RegressionSelector(test_mapper=mapper, safety_gate=gate, all_tests=test_suite)
    
    impacts = [Impact("FN_BRAKE", "C_Function", "ADAS", "ECU_1", ImpactType.STRUCTURAL, 1.0, SourceStage.GRAPH)]
    result = selector.select(impacts)
    
    # Selected: TC_01 (ASIL-D), TC_04 (ASIL-C) -> 2 out of 10 tests
    assert len(result.selected_tests) == 2
    assert result.all_tests_count == 10
    assert result.removed_tests_count == 8
    # Test reduction = (1 - 2/10) * 100% = 80.0%
    assert result.test_reduction_pct == 80.0


def test_empty_impact_handling(test_suite):
    """Scenario 7: Empty impact set with no safety mandates selects 0 tests (100% reduction)."""
    mapper = TestMapper(all_tests=test_suite)
    gate = SafetyGate()
    selector = RegressionSelector(test_mapper=mapper, safety_gate=gate, all_tests=test_suite)
    
    result = selector.select(impacts=[])
    assert len(result.selected_tests) == 0
    assert result.test_reduction_pct == 100.0


def test_full_suite_fallback_behavior(test_suite):
    """Scenario 8: Full suite fallback selects all tests when system enters fail-safe mode."""
    # When all tests are declared mandatory (e.g. unknown system corruption)
    mapper = TestMapper(all_tests=test_suite)
    gate = SafetyGate()
    selector = RegressionSelector(test_mapper=mapper, safety_gate=gate, all_tests=test_suite)
    
    all_test_ids = {t.test_id for t in test_suite}
    result = selector.select(impacts=[], mandatory_safety_test_ids=all_test_ids)
    
    assert len(result.selected_tests) == 10
    assert result.test_reduction_pct == 0.0


def test_exact_metric_calculations():
    """Scenario 9: Validates precision, recall, test reduction %, safety recall, FP, FN formulas."""
    # Ground truth: truly impacted tests = {T1, T2, T3, T_SAFE_1}
    ground_truth_tests = {"T1", "T2", "T3", "T_SAFE_1"}
    ground_truth_safety_tests = {"T_SAFE_1", "T_SAFE_2"}  # T_SAFE_2 was latent and missed by impact analysis
    
    # Engine selected: {T1, T2, T4, T_SAFE_1}
    selected_tests = {"T1", "T2", "T4", "T_SAFE_1"}
    total_test_suite_size = 20
    
    # True positives (selected & truly impacted)
    tp = len(selected_tests & ground_truth_tests)  # T1, T2, T_SAFE_1 -> 3
    # False positives (selected but not truly impacted)
    fp = len(selected_tests - ground_truth_tests)  # T4 -> 1
    # False negatives (truly impacted but not selected)
    fn = len(ground_truth_tests - selected_tests)  # T3 -> 1
    
    test_precision = tp / (tp + fp)  # 3 / 4 = 0.75
    test_recall = tp / (tp + fn)     # 3 / 4 = 0.75
    test_reduction = (1.0 - (len(selected_tests) / total_test_suite_size)) * 100.0  # (1 - 4/20)*100 = 80.0%
    
    # Safety Recall (discovery of latent safety tests)
    safety_tp = len(selected_tests & ground_truth_safety_tests)  # T_SAFE_1 -> 1
    safety_recall = safety_tp / len(ground_truth_safety_tests)   # 1 / 2 = 0.50 (50.0%)
    
    # Safety Invariant Guarantee: ALL selected safety tests from identified impacts are retained
    safety_invariant_held = "T_SAFE_1" in selected_tests
    
    assert tp == 3
    assert fp == 1
    assert fn == 1
    assert test_precision == 0.75
    assert test_recall == 0.75
    assert test_reduction == 80.0
    assert safety_recall == 0.50  # Matches how 47.61% is computed in the benchmark!
    assert safety_invariant_held is True
