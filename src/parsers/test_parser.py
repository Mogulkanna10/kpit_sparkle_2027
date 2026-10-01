"""
Test Case Parser
Ingests verification test suites with ASIL safety classifications and target artifact mappings.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import csv
import yaml

from src.graph.schema import GraphNode, GraphEdge, NodeType, RelationType, SafetyLevel


@dataclass
class TestRecord:
    __test__ = False
    test_id: str
    description: str
    artifact_targets: List[str]
    safety_class: str  # QM, ASIL_A, ASIL_B, ASIL_C, ASIL_D
    subsystem: str
    ecu: str
    source_file: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class TestParser:
    """Parses test definitions and suites across JSON, YAML, and CSV formats."""
    __test__ = False

    def __init__(self, project_name: str = "ADAS", **kwargs):
        self.project_name = project_name

    def parse_file(self, file_path: Path) -> Tuple[List[GraphNode], List[GraphEdge]]:
        records = self.parse_records(file_path, default_subsystem=self.project_name)
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        for t in records:
            lvl = SafetyLevel[t.safety_class] if t.safety_class in SafetyLevel.__members__ else SafetyLevel.QM
            nodes.append(GraphNode(
                id=t.test_id,
                type=NodeType.TEST,
                name=t.test_id,
                subsystem=t.subsystem,
                ecu=t.ecu,
                source_file=str(file_path),
                file_path=str(file_path),
                project=t.subsystem,
                safety_level=lvl,
                metadata={"description": t.description}
            ))
            for tgt in t.artifact_targets:
                edges.append(GraphEdge(
                    source=t.test_id,
                    target=tgt,
                    relation=RelationType.VERIFIES,
                    provenance="Test Mapping Specification"
                ))

        return nodes, edges

    @staticmethod
    def parse_records(file_path: Path, default_subsystem: str = "ADAS", default_ecu: str = "ECU_1") -> List[TestRecord]:
        file_path = Path(file_path)
        if not file_path.exists():
            return []

        suffix = file_path.suffix.lower()
        records: List[TestRecord] = []

        if suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            items = data if isinstance(data, list) else data.get("tests", data.get("test_cases", [data]))
            for it in items:
                raw_targets = []
                for k in ["artifact_targets", "targets", "target_artifacts", "target_functions", "target_swcs", "target_requirements"]:
                    v = it.get(k)
                    if v:
                        if isinstance(v, list):
                            raw_targets.extend(v)
                        elif isinstance(v, str):
                            raw_targets.extend([s.strip() for s in v.split(";") if s.strip()])
                targets = list(set(raw_targets))

                records.append(TestRecord(
                    test_id=it.get("id") or it.get("test_id", "TC_UNKNOWN"),
                    description=it.get("description", it.get("name", "")),
                    artifact_targets=targets,
                    safety_class=it.get("safety_class", it.get("safety_level", it.get("asil", "QM"))),
                    subsystem=it.get("subsystem", default_subsystem),
                    ecu=it.get("ecu", default_ecu),
                    source_file=str(file_path),
                    metadata=it.get("metadata", {})
                ))

        elif suffix in [".yaml", ".yml"]:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            items = data if isinstance(data, list) else data.get("tests", [data])
            for it in items:
                records.append(TestRecord(
                    test_id=it.get("id") or it.get("test_id", "TC_UNKNOWN"),
                    description=it.get("description", ""),
                    artifact_targets=it.get("artifact_targets", []),
                    safety_class=it.get("safety_class", "QM"),
                    subsystem=it.get("subsystem", default_subsystem),
                    ecu=it.get("ecu", default_ecu),
                    source_file=str(file_path),
                    metadata={}
                ))

        elif suffix == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    t_str = row.get("artifact_targets", row.get("targets", ""))
                    targets = [t.strip() for t in t_str.split(";") if t.strip()] if t_str else []
                    records.append(TestRecord(
                        test_id=row.get("id") or row.get("test_id", "TC_UNKNOWN"),
                        description=row.get("description", row.get("name", "")),
                        artifact_targets=targets,
                        safety_class=row.get("safety_class", row.get("asil", "QM")),
                        subsystem=row.get("subsystem", default_subsystem),
                        ecu=row.get("ecu", default_ecu),
                        source_file=str(file_path),
                        metadata={}
                    ))

        return records
