"""
Engineering Graph Schema & Typed Data Models
Defines core node types, edge relations, and provenance metadata for AUTOSAR systems.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List


class NodeType(str, Enum):
    REQUIREMENT = "Requirement"
    SOFTWARE_COMPONENT = "SoftwareComponent"
    SWC = "SoftwareComponent"
    PORT = "Port"
    INTERFACE = "Interface"
    DATA_ELEMENT = "DataElement"
    RUNNABLE = "Runnable"
    C_FUNCTION = "C_Function"
    C_VARIABLE = "C_Variable"
    TEST = "Test"
    DIAGNOSTIC_EVENT = "DiagnosticEvent"


class RelationType(str, Enum):
    MAPS_TO = "MAPS_TO"
    OWNS = "OWNS"
    CALLS = "CALLS"
    READS = "READS"
    WRITES = "WRITES"
    PROVIDES = "PROVIDES"
    REQUIRES = "REQUIRES"
    IMPLEMENTS = "IMPLEMENTS"
    VERIFIES = "VERIFIES"
    TESTS = "TESTS"
    DEPENDS_ON = "DEPENDS_ON"
    TRIGGERS = "TRIGGERS"


class SafetyLevel(str, Enum):
    QM = "QM"
    ASIL_A = "ASIL_A"
    ASIL_B = "ASIL_B"
    ASIL_C = "ASIL_C"
    ASIL_D = "ASIL_D"
    SAFETY_CRITICAL = "ASIL_D"


class GraphNode:
    def __init__(self,
                 id: str,
                 type: Any,
                 name: str = "",
                 subsystem: str = "ADAS",
                 ecu: str = "ECU_1",
                 source_file: str = "",
                 source_location: str = "",
                 safety_level: SafetyLevel = SafetyLevel.QM,
                 metadata: Optional[Dict[str, Any]] = None,
                 file_path: str = "",
                 project: str = ""):
        self.id = id
        self.type = type
        self.name = name or id
        self.subsystem = subsystem or project or "ADAS"
        self.project = self.subsystem
        self.ecu = ecu
        self.source_file = source_file or file_path or ""
        self.file_path = self.source_file
        self.source_location = source_location
        self.safety_level = safety_level
        self.metadata = metadata or {}

    @property
    def description(self):
        return self.metadata.get("description", self.name)

    @property
    def properties(self):
        return self.metadata


class GraphEdge:
    def __init__(self,
                 source: Optional[str] = None,
                 target: Optional[str] = None,
                 relation: Any = RelationType.DEPENDS_ON,
                 provenance: str = "Deterministic Parser",
                 confidence: float = 1.0,
                 metadata: Optional[Dict[str, Any]] = None,
                 edge_type: Any = None,
                 weight: float = 1.0,
                 source_id: Optional[str] = None,
                 target_id: Optional[str] = None,
                 source_file: str = ""):
        self.source = source or source_id or ""
        self.target = target or target_id or ""
        self.source_id = self.source
        self.target_id = self.target
        self.relation = relation if relation != RelationType.DEPENDS_ON else (edge_type or relation)
        self.edge_type = self.relation
        self.provenance = provenance
        self.confidence = confidence
        self.weight = weight
        self.source_file = source_file
        self.metadata = metadata or {}


# Backward-compatible aliases
Node = GraphNode
Edge = GraphEdge
EdgeType = RelationType
