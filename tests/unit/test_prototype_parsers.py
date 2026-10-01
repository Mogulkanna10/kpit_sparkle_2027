"""
Unit Tests for AURA-Impact Prototype Parsers
"""
import pytest
from pathlib import Path
from src.parsers.cpp_parser import CppTreeSitterParser
from src.parsers.arxml_parser import AutosarARXMLParser
from src.parsers.requirement_parser import RequirementParser
from src.parsers.test_parser import TestParser

DEMO_DIR = Path("examples/demo_repo")


def test_cpp_parser():
    parser = CppTreeSitterParser()
    fns, vars_found = parser.parse_records(DEMO_DIR / "src/aeb_controller.c")
    fn_names = [f.name for f in fns]
    assert "C_Function_CalculateTTC" in fn_names
    assert "C_Function_TriggerBrake" in fn_names
    assert len(fns) >= 2


def test_arxml_parser():
    parser = AutosarARXMLParser()
    data = parser.parse_records(DEMO_DIR / "arxml/aeb_swc.arxml")
    swcs = data["swcs"]
    assert len(swcs) == 1
    assert swcs[0].name == "SWC_AEB"
    assert len(swcs[0].ports) == 2
    assert len(swcs[0].runnables) == 1


def test_requirement_parser():
    reqs = RequirementParser.parse_records(DEMO_DIR / "requirements/reqs.json")
    assert len(reqs) == 4
    req_ids = [r.req_id for r in reqs]
    assert "REQ_AEB_001" in req_ids
    assert "REQ_AEB_014" in req_ids


def test_test_parser():
    tests = TestParser.parse_records(DEMO_DIR / "tests/test_suite.json")
    assert len(tests) == 4
    t_ids = [t.test_id for t in tests]
    assert "TC_AEB_001" in t_ids
    assert "TC_AEB_002" in t_ids
