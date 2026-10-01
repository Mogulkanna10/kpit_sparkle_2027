"""
Unit tests for AUTOSAR parsers
"""
import pytest
from pathlib import Path
from src.parsers.requirement_parser import RequirementParser
from src.parsers.arxml_parser import ARXMLParser
from src.parsers.cpp_parser import CppParser
from src.parsers.test_parser import TestParser
from src.graph.schema import NodeType


def test_requirement_parser():
    parser = RequirementParser("ADAS")
    req_file = Path("data/projects/adas/requirements/adas_requirements.json")
    if req_file.exists():
        nodes, edges = parser.parse_file(req_file)
        assert len(nodes) >= 50
        assert all(n.type == NodeType.REQUIREMENT for n in nodes)
        assert len(edges) > 0


def test_arxml_parser():
    parser = ARXMLParser("ADAS")
    arxml_file = Path("data/projects/adas/arxml/SWC_AEB.arxml")
    if arxml_file.exists():
        nodes, edges = parser.parse_file(arxml_file)
        assert len(nodes) > 0
        swc_nodes = [n for n in nodes if n.type == NodeType.SWC]
        assert len(swc_nodes) >= 1
        assert swc_nodes[0].id == "SWC_AEB"


def test_cpp_parser():
    parser = CppParser("ADAS")
    c_file = Path("data/projects/adas/src/adas_controller.c")
    if c_file.exists():
        nodes, edges = parser.parse_file(c_file)
        assert len(nodes) >= 80
        assert all(n.type == NodeType.C_FUNCTION for n in nodes)
        assert len(edges) > 0


def test_test_parser():
    parser = TestParser("ADAS")
    t_file = Path("data/projects/adas/tests/test_adas.json")
    if t_file.exists():
        nodes, edges = parser.parse_file(t_file)
        assert len(nodes) >= 80
        assert all(n.type == NodeType.TEST for n in nodes)
        assert len(edges) > 0
