"""
Automotive Change Detector
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class ChangeContext:
    change_id: str
    project: str
    source_artifact: str
    target_node_id: Optional[str]
    artifact_type: str  # "REQUIREMENT", "ARXML", "C_CODE", "TEST", "DOC", etc.
    before_content: str
    after_content: str
    diff_text: str
    change_semantics: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChangeDetector:
    def parse_mutation_record(self, record: Dict[str, Any]) -> ChangeContext:
        return ChangeContext(
            change_id=record.get("mutation_id", "CHG_UNKNOWN"),
            project=record.get("project_id", "ADAS"),
            source_artifact=record.get("source_artifact", ""),
            target_node_id=record.get("target_node_id"),
            artifact_type=record.get("artifact_type", "REQUIREMENT"),
            before_content=record.get("before_state", ""),
            after_content=record.get("after_state", ""),
            diff_text=record.get("diff", f"- {record.get('before_state','')}\n+ {record.get('after_state','')}"),
            change_semantics=record.get("intended_change_semantics", ""),
            metadata=record.get("metadata", {})
        )
