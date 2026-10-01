"""
Impact Set Union Engine
Implements strict mathematical set union: S_final = S_struct UNION S_semantic.
Strictly forbids weighted score fusion.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Set, Optional


class ImpactType(str, Enum):
    STRUCTURAL = "STRUCTURAL"
    SEMANTIC = "SEMANTIC"
    UNKNOWN = "UNKNOWN"


class SourceStage(str, Enum):
    GRAPH = "GRAPH"
    SEMANTIC = "SEMANTIC"


@dataclass
class Impact:
    artifact_id: str
    artifact_type: str
    subsystem: str
    ecu: str
    impact_type: ImpactType
    confidence: float
    source_stage: SourceStage
    evidence: Dict[str, Any] = field(default_factory=dict)
    source_file: str = ""
    source_location: str = ""


class ImpactUnion:
    """Combines deterministic structural impacts and validated semantic recoveries via strict set union."""

    @staticmethod
    def compute_union(structural_impacts: List[Impact], semantic_impacts: List[Impact]) -> List[Impact]:
        final_map: Dict[str, Impact] = {}

        # 1. Structural impacts take precedence
        for imp in structural_impacts:
            final_map[imp.artifact_id] = imp

        # 2. Add non-duplicate semantic recoveries
        for imp in semantic_impacts:
            if imp.artifact_id not in final_map:
                final_map[imp.artifact_id] = imp

        return list(final_map.values())
