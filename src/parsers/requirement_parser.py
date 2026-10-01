"""
Requirement Parser
Supports TXT, Markdown, CSV, and JSON requirements with ASIL and explicit trace links.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import csv
import re

from src.graph.schema import GraphNode, GraphEdge, NodeType, RelationType, SafetyLevel


@dataclass
class RequirementRecord:
    req_id: str
    title: str
    description: str
    subsystem: str
    ecu: str
    asil: str  # QM, ASIL_A, ASIL_B, ASIL_C, ASIL_D
    trace_links: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RequirementParser:
    """Ingests requirements from various structured and semi-structured formats."""

    def __init__(self, project_name: str = "ADAS", **kwargs):
        self.project_name = project_name

    def parse_file(self, file_path: Path) -> Tuple[List[GraphNode], List[GraphEdge]]:
        records = self.parse_records(file_path, default_subsystem=self.project_name)
        nodes = []
        edges = []
        for r in records:
            lvl = SafetyLevel[r.asil] if r.asil in SafetyLevel.__members__ else SafetyLevel.QM
            nodes.append(GraphNode(
                id=r.req_id,
                type=NodeType.REQUIREMENT,
                name=r.title or r.req_id,
                subsystem=r.subsystem,
                ecu=r.ecu,
                source_file=str(file_path),
                file_path=str(file_path),
                project=r.subsystem,
                safety_level=lvl,
                metadata={"description": r.description}
            ))
            for tgt in r.trace_links:
                edges.append(GraphEdge(
                    source=r.req_id,
                    target=tgt,
                    relation=RelationType.MAPS_TO,
                    provenance="Requirement Trace Link"
                ))
        return nodes, edges

    @staticmethod
    def parse_records(file_path: Path, default_subsystem: str = "ADAS", default_ecu: str = "ECU_1") -> List[RequirementRecord]:
        file_path = Path(file_path)
        if not file_path.exists():
            return []

        suffix = file_path.suffix.lower()
        records: List[RequirementRecord] = []

        if suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            items = data if isinstance(data, list) else data.get("requirements", [data])
            for it in items:
                records.append(RequirementRecord(
                    req_id=it.get("id") or it.get("req_id") or it.get("requirement_id", "REQ_UNKNOWN"),
                    title=it.get("title", ""),
                    description=it.get("description", it.get("text", "")),
                    subsystem=it.get("subsystem", default_subsystem),
                    ecu=it.get("ecu", default_ecu),
                    asil=it.get("asil") or it.get("asil_level") or it.get("safety_level", "QM"),
                    trace_links=it.get("trace_links") or it.get("mapped_artifacts") or it.get("mapped_swcs") or it.get("verification_tests") or [],
                    metadata=it.get("metadata", {})
                ))

        elif suffix == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trace_str = row.get("trace_links", row.get("mapped_artifacts", ""))
                    links = [l.strip() for l in trace_str.split(";") if l.strip()] if trace_str else []
                    records.append(RequirementRecord(
                        req_id=row.get("id") or row.get("req_id", "REQ_UNKNOWN"),
                        title=row.get("title", ""),
                        description=row.get("description", row.get("text", "")),
                        subsystem=row.get("subsystem", default_subsystem),
                        ecu=row.get("ecu", default_ecu),
                        asil=row.get("asil", "QM"),
                        trace_links=links,
                        metadata={}
                    ))

        elif suffix in [".md", ".txt"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            pattern = re.compile(r"^(#+)\s*([A-Za-z0-9_\-]+)(.*?)(?=(?:^#+|\Z))", re.MULTILINE | re.DOTALL)
            matches = list(pattern.finditer(text))
            if matches:
                for m in matches:
                    req_id = m.group(2).strip()
                    body = m.group(3).strip()
                    asil_match = re.search(r"ASIL[-_]([ABCDQM])", body, re.IGNORECASE)
                    asil = f"ASIL_{asil_match.group(1).upper()}" if asil_match else "QM"
                    records.append(RequirementRecord(
                        req_id=req_id,
                        title=req_id,
                        description=body,
                        subsystem=default_subsystem,
                        ecu=default_ecu,
                        asil=asil,
                        trace_links=[]
                    ))
            else:
                records.append(RequirementRecord(
                    req_id=f"REQ_{file_path.stem}",
                    title=file_path.stem,
                    description=text[:500],
                    subsystem=default_subsystem,
                    ecu=default_ecu,
                    asil="QM"
                ))

        return records
