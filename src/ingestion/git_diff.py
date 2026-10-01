"""
Git Diff Ingestion & Change Extraction
Parses diffs, patches, or change JSON specifications into ChangeContext objects.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import json
import re
from pathlib import Path


@dataclass
class ChangedArtifact:
    artifact_id: str
    artifact_type: str
    subsystem: str
    ecu: str
    change_type: str  # ADD, MODIFY, DELETE
    before_content: str = ""
    after_content: str = ""
    diff_text: str = ""
    change_semantics: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class GitDiffParser:
    """Parses git diff outputs or change files into ChangedArtifact structures."""

    @staticmethod
    def parse_change_file(file_path: Path) -> List[ChangedArtifact]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Change file not found: {file_path}")

        if file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                items = data.get("changes", [data])
            elif isinstance(data, list):
                items = data
            else:
                items = []

            results = []
            for item in items:
                results.append(ChangedArtifact(
                    artifact_id=item.get("artifact_id") or item.get("change_id") or item.get("source_artifact", "UNKNOWN_CHANGE"),
                    artifact_type=item.get("artifact_type", "Requirement"),
                    subsystem=item.get("subsystem", item.get("project", "ADAS")),
                    ecu=item.get("ecu", "ECU_1"),
                    change_type=item.get("change_type", "MODIFY"),
                    before_content=item.get("before_content", ""),
                    after_content=item.get("after_content", item.get("query_text", "")),
                    diff_text=item.get("diff_text", ""),
                    change_semantics=item.get("change_semantics", item.get("query_text", item.get("after_content", ""))),
                    metadata=item.get("metadata", {})
                ))
            return results

        elif file_path.suffix in [".diff", ".patch", ".txt"]:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_diff = f.read()

            return [ChangedArtifact(
                artifact_id=f"DIFF_{file_path.stem}",
                artifact_type="SourceCode",
                subsystem="Powertrain",
                ecu="ECU_Primary",
                change_type="MODIFY",
                diff_text=raw_diff,
                change_semantics=raw_diff[:500],
                metadata={"file_name": file_path.name}
            )]
        else:
            raise ValueError(f"Unsupported change file format: {file_path.suffix}")
