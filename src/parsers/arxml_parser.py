"""
AUTOSAR ARXML Parser using lxml
Extracts SoftwareComponents (SWCs), Ports, Interfaces, DataElements, Runnables, and explicit relationships.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from lxml import etree

from src.graph.schema import GraphNode, GraphEdge, NodeType, RelationType, SafetyLevel


@dataclass
class ARXMLRunnable:
    name: str
    symbol: str
    swc_name: str
    period: float = 0.0


@dataclass
class ARXMLPort:
    name: str
    port_type: str  # P_PORT, R_PORT
    interface_ref: str
    swc_name: str


@dataclass
class ARXMLInterface:
    name: str
    interface_type: str  # SENDER_RECEIVER, CLIENT_SERVER
    data_elements: List[str] = field(default_factory=list)


@dataclass
class ARXMLSWC:
    name: str
    swc_type: str
    ecu: str
    subsystem: str
    ports: List[ARXMLPort] = field(default_factory=list)
    runnables: List[ARXMLRunnable] = field(default_factory=list)


class AutosarARXMLParser:
    """Parses AUTOSAR ARXML files deterministically without semantic inference."""

    def __init__(self, project_name: str = "ADAS", **kwargs):
        self.project_name = project_name

    def parse_file(self, file_path: Path) -> Tuple[List[GraphNode], List[GraphEdge]]:
        records = self.parse_records(file_path, subsystem=self.project_name)
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        for swc in records.get("swcs", []):
            swc_node = GraphNode(
                id=swc.name,
                type=NodeType.SWC,
                name=swc.name,
                subsystem=swc.subsystem,
                ecu=swc.ecu,
                source_file=str(file_path),
                file_path=str(file_path),
                project=swc.subsystem
            )
            nodes.append(swc_node)

            for port in swc.ports:
                p_node = GraphNode(
                    id=port.name,
                    type=NodeType.PORT,
                    name=port.name,
                    subsystem=swc.subsystem,
                    ecu=swc.ecu,
                    source_file=str(file_path),
                    file_path=str(file_path),
                    project=swc.subsystem
                )
                nodes.append(p_node)
                edges.append(GraphEdge(
                    source=swc.name,
                    target=port.name,
                    relation=RelationType.PROVIDES if port.port_type == "P_PORT" else RelationType.REQUIRES,
                    provenance="ARXML Port Prototype"
                ))

            for run in swc.runnables:
                r_node = GraphNode(
                    id=run.name,
                    type=NodeType.RUNNABLE,
                    name=run.name,
                    subsystem=swc.subsystem,
                    ecu=swc.ecu,
                    source_file=str(file_path),
                    file_path=str(file_path),
                    project=swc.subsystem
                )
                nodes.append(r_node)
                edges.append(GraphEdge(
                    source=swc.name,
                    target=run.name,
                    relation=RelationType.OWNS,
                    provenance="ARXML Runnable Entity"
                ))

        return nodes, edges

    def parse_records(self, file_path: Path, subsystem: str = "ADAS", ecu: str = "ECU_1") -> Dict[str, Any]:
        file_path = Path(file_path)
        if not file_path.exists():
            return {"swcs": [], "interfaces": []}

        try:
            tree = etree.parse(str(file_path))
            root = tree.getroot()
        except Exception:
            return {"swcs": [], "interfaces": []}

        namespaces = root.nsmap
        ns = {"ar": namespaces.get(None, "http://autosar.org/schema/r4.0")} if None in namespaces else {}

        swcs: List[ARXMLSWC] = []
        interfaces: List[ARXMLInterface] = []

        swc_nodes = root.findall(".//APPLICATION-SW-COMPONENT-TYPE", namespaces=ns) + \
                    root.findall(".//SENSOR-ACTUATOR-SW-COMPONENT-TYPE", namespaces=ns) + \
                    root.findall(".//COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE", namespaces=ns) + \
                    root.findall(".//APPLICATION-SOFTWARE-COMPONENT-TYPE", namespaces=ns)

        if not swc_nodes:
            for elem in root.iter():
                tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if "SW-COMPONENT-TYPE" in tag:
                    swc_nodes.append(elem)

        for swc_elem in swc_nodes:
            short_name_elem = swc_elem.find("SHORT-NAME", namespaces=ns)
            if short_name_elem is None:
                for c in swc_elem:
                    if (c.tag.split("}")[-1] if "}" in c.tag else c.tag) == "SHORT-NAME":
                        short_name_elem = c
                        break

            swc_name = short_name_elem.text if short_name_elem is not None else swc_elem.get("name", "SWC_Unknown")
            swc_type = swc_elem.tag.split("}")[-1] if "}" in swc_elem.tag else swc_elem.tag

            ports: List[ARXMLPort] = []
            runnables: List[ARXMLRunnable] = []

            for p in swc_elem.iter():
                tag = p.tag.split("}")[-1] if "}" in p.tag else p.tag
                if tag in ["P-PORT-PROTOTYPE", "PROVIDED-PORT", "P-PORT"]:
                    p_name = self._get_short_name(p) or f"{swc_name}_PPort"
                    p_if = self._get_interface_ref(p) or "DefaultInterface"
                    ports.append(ARXMLPort(name=p_name, port_type="P_PORT", interface_ref=p_if, swc_name=swc_name))
                elif tag in ["R-PORT-PROTOTYPE", "REQUIRED-PORT", "R-PORT"]:
                    p_name = self._get_short_name(p) or f"{swc_name}_RPort"
                    p_if = self._get_interface_ref(p) or "DefaultInterface"
                    ports.append(ARXMLPort(name=p_name, port_type="R_PORT", interface_ref=p_if, swc_name=swc_name))

            for r in swc_elem.iter():
                tag = r.tag.split("}")[-1] if "}" in r.tag else r.tag
                if "RUNNABLE-ENTITY" in tag:
                    r_name = self._get_short_name(r) or f"{swc_name}_Runnable"
                    r_sym = r.findtext("SYMBOL", default=r_name)
                    runnables.append(ARXMLRunnable(name=r_name, symbol=r_sym, swc_name=swc_name))

            swcs.append(ARXMLSWC(
                name=swc_name,
                swc_type=swc_type,
                ecu=ecu,
                subsystem=subsystem,
                ports=ports,
                runnables=runnables
            ))

        for if_elem in root.iter():
            tag = if_elem.tag.split("}")[-1] if "}" in if_elem.tag else if_elem.tag
            if "INTERFACE" in tag and "PORT" not in tag:
                if_name = self._get_short_name(if_elem)
                if if_name:
                    data_elements = []
                    for de in if_elem.iter():
                        de_tag = de.tag.split("}")[-1] if "}" in de.tag else de.tag
                        if "DATA-ELEMENT" in de_tag or "VARIABLE-DATA-PROTOTYPE" in de_tag:
                            de_name = self._get_short_name(de)
                            if de_name:
                                data_elements.append(de_name)
                    interfaces.append(ARXMLInterface(
                        name=if_name,
                        interface_type="SENDER_RECEIVER" if "SENDER" in tag else "CLIENT_SERVER",
                        data_elements=data_elements
                    ))

        return {"swcs": swcs, "interfaces": interfaces}

    def _get_short_name(self, elem) -> Optional[str]:
        for c in elem:
            tag = c.tag.split("}")[-1] if "}" in c.tag else c.tag
            if tag == "SHORT-NAME" and c.text:
                return c.text.strip()
        return elem.get("name")

    def _get_interface_ref(self, elem) -> Optional[str]:
        for c in elem.iter():
            tag = c.tag.split("}")[-1] if "}" in c.tag else c.tag
            if "INTERFACE-REF" in tag and c.text:
                return c.text.strip().split("/")[-1]
        return None


# Backward-compatible alias
ARXMLParser = AutosarARXMLParser
