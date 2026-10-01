"""
Engineering Graph Builder Script
Parses requirements, ARXML, C/C++ source code, and tests across all projects.
Constructs heterogeneous engineering graphs with full edge provenance.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Ensure workspace root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.graph.builder import EngineeringGraph
from src.parsers.requirement_parser import RequirementParser
from src.parsers.arxml_parser import ARXMLParser
from src.parsers.cpp_parser import CppParser
from src.parsers.test_parser import TestParser


def build_project_graph(project_name: str, project_dir: Path) -> EngineeringGraph:
    eng_graph = EngineeringGraph(name=project_name)
    
    req_parser = RequirementParser(project_name=project_name)
    arxml_parser = ARXMLParser(project_name=project_name)
    cpp_parser = CppParser(project_name=project_name)
    test_parser = TestParser(project_name=project_name)

    # 1. Parse Requirements
    req_files = list((project_dir / "requirements").glob("*.json"))
    for rf in req_files:
        nodes, edges = req_parser.parse_file(rf)
        for n in nodes:
            eng_graph.add_node(n)
        for e in edges:
            eng_graph.add_edge(e)

    # 2. Parse ARXML
    arxml_files = list((project_dir / "arxml").glob("*.arxml"))
    for af in arxml_files:
        nodes, edges = arxml_parser.parse_file(af)
        for n in nodes:
            eng_graph.add_node(n)
        for e in edges:
            eng_graph.add_edge(e)

    # 3. Parse C Code
    c_files = list((project_dir / "src").glob("*.c")) + list((project_dir / "src").glob("*.cpp"))
    for cf in c_files:
        nodes, edges = cpp_parser.parse_file(cf)
        for n in nodes:
            eng_graph.add_node(n)
        for e in edges:
            eng_graph.add_edge(e)

    # 4. Parse Tests
    test_files = list((project_dir / "tests").glob("*.json"))
    for tf in test_files:
        nodes, edges = test_parser.parse_file(tf)
        for n in nodes:
            eng_graph.add_node(n)
        for e in edges:
            eng_graph.add_edge(e)

    return eng_graph


def main():
    base_dir = Path("data/projects")
    out_dir = Path("data/normalized")
    out_dir.mkdir(parents=True, exist_ok=True)

    projects = ["adas", "powertrain", "battery_ev"]
    graphs = {}

    for proj in projects:
        p_dir = base_dir / proj
        if p_dir.exists():
            print(f"Building engineering graph for {proj}...")
            g = build_project_graph(proj.upper(), p_dir)
            graphs[proj] = g
            summary = g.summary()
            print(f"  [OK] Nodes: {summary['total_nodes']}, Edges: {summary['total_edges']}")
            print(f"  Node types: {summary['node_type_breakdown']}")

            # Save normalized graph
            with open(out_dir / f"{proj}_graph.json", "w", encoding="utf-8") as f:
                json.dump(g.to_dict(), f, indent=2)

    print("[OK] All project engineering graphs successfully built and saved to data/normalized/")


if __name__ == "__main__":
    main()
