"""
Controlled Automotive Mutation Generator across 25 Mutation Categories (M01-M25)
"""
import json
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class MutationRecord:
    mutation_id: str
    project_id: str
    change_type: str  # "M01", "M02", ..., "M25"
    category_name: str
    source_artifact: str
    target_node_id: str
    artifact_type: str  # "REQUIREMENT", "ARXML", "C_CODE", "TEST", "DOC"
    before_state: str
    after_state: str
    diff: str
    intended_change_semantics: str
    expected_impact_scope: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MutationGenerator:
    def __init__(self, seed: int = 2002):
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_mutations_for_project(
        self,
        project_id: str,
        project_graph_dict: Dict[str, Any]
    ) -> List[MutationRecord]:
        mutations: List[MutationRecord] = []
        nodes = project_graph_dict.get("nodes", [])

        req_nodes = [n for n in nodes if n.get("type") == "Requirement"]
        swc_nodes = [n for n in nodes if n.get("type") == "SWC"]
        func_nodes = [n for n in nodes if n.get("type") == "C_Function"]
        test_nodes = [n for n in nodes if n.get("type") == "Test"]
        iface_nodes = [n for n in nodes if n.get("type") == "Interface"]
        de_nodes = [n for n in nodes if n.get("type") == "DataElement"]

        # Ensure we have items to mutate
        req_count = len(req_nodes)
        func_count = len(func_nodes)
        test_count = len(test_nodes)

        # Helper to pick safely
        def pick(lst, default_id="NODE_01"):
            return self.rng.choice(lst) if lst else {"id": default_id, "name": default_id, "description": "", "file_path": ""}

        mutation_defs = [
            ("M01", "Numeric requirement change", "REQUIREMENT"),
            ("M02", "Threshold change", "REQUIREMENT"),
            ("M03", "Semantic wording change", "REQUIREMENT"),
            ("M04", "Requirement synonym replacement", "REQUIREMENT"),
            ("M05", "Requirement constraint addition", "REQUIREMENT"),
            ("M06", "ARXML datatype change", "ARXML"),
            ("M07", "ARXML scaling change", "ARXML"),
            ("M08", "Interface field change", "ARXML"),
            ("M09", "Interface version change", "ARXML"),
            ("M10", "C function signature change", "C_CODE"),
            ("M11", "C constant change", "C_CODE"),
            ("M12", "Function dependency change", "C_CODE"),
            ("M13", "Variable dependency change", "C_CODE"),
            ("M14", "Test requirement modification", "TEST"),
            ("M15", "Unrelated/no-impact change", "C_CODE"),
            ("M16", "Indirect dependency change", "C_CODE"),
            ("M17", "Long-chain dependency change", "REQUIREMENT"),
            ("M18", "Cross-domain Req->ARXML->C->Test change", "REQUIREMENT"),
            ("M19", "Misleading semantic similarity", "REQUIREMENT"),
            ("M20", "Multiple simultaneous changes", "C_CODE"),
            ("M21", "Lexical renaming", "C_CODE"),
            ("M22", "Structural rename with same semantics", "C_CODE"),
            ("M23", "Semantic requirement change with little textual overlap", "REQUIREMENT"),
            ("M24", "Dead-code modification", "C_CODE"),
            ("M25", "Documentation-only change", "DOC"),
        ]

        # Generate multiple controlled variations per category to ensure >= 40-50 mutations per project (120-150 total)
        mut_idx = 1
        for repeat in range(2):  # 2 passes x 25 categories = 50 mutations per project
            for code, cat_name, art_type in mutation_defs:
                m_id = f"{project_id}_{code}_{repeat+1:02d}"

                if art_type == "REQUIREMENT":
                    r = pick(req_nodes)
                    nid = r["id"]
                    fpath = r.get("file_path", f"requirements/{project_id.lower()}_reqs.json")
                    desc = r.get("description", "Safety requirement")

                    if code == "M01":
                        before = f"{desc} [Safety distance: 20 meters]"
                        after = f"{desc} [Safety distance: 15 meters]"
                        sem = "Tighter distance threshold for emergency braking"
                    elif code == "M02":
                        before = f"{desc} [TTC limit: 1.8 seconds]"
                        after = f"{desc} [TTC limit: 1.4 seconds]"
                        sem = "Reduced time-to-collision trigger threshold"
                    elif code == "M03":
                        before = f"The vehicle shall initiate emergency deceleration upon obstacle detection."
                        after = f"The automated braking system shall execute autonomous stopping when a collision hazard is identified."
                        sem = "Paraphrased requirement semantics"
                    elif code == "M04":
                        before = f"Calculate vehicle speed and apply braking pressure."
                        after = f"Compute longitudinal velocity and exert deceleration force."
                        sem = "Synonym replacement preserving technical intent"
                    elif code == "M05":
                        before = f"{desc}"
                        after = f"{desc} under condition that ambient temperature is above -10C and battery SoC > 15%."
                        sem = "Operational condition and environmental constraint addition"
                    elif code == "M17":
                        before = f"System requirement {nid} root specification."
                        after = f"System requirement {nid} propagated down through SWC, ports, runnables, and RTE."
                        sem = "Long-chain multi-tier downstream impact"
                    elif code == "M18":
                        before = f"Cross-domain constraint on {nid}."
                        after = f"Cross-domain update impacting sensor input, control computation, and actuator output."
                        sem = "Cascading cross-domain impact"
                    elif code == "M19":
                        before = f"Calibrate braking hydraulic threshold."
                        after = f"Calibrate parking brake pressure hold threshold."
                        sem = "Misleading semantic similarity across distinct sub-functions"
                    elif code == "M23":
                        before = f"Maintain headway gap in adaptive cruise mode."
                        after = f"Radar-guided distance tracking regulation."
                        sem = "Semantic change with near-zero lexical token overlap"
                    else:
                        before = desc
                        after = f"{desc} (Updated specification)"
                        sem = f"Standard requirement revision for {code}"

                elif art_type == "ARXML":
                    iface = pick(iface_nodes)
                    de = pick(de_nodes)
                    nid = iface["id"] if "Interface" in code else de["id"]
                    fpath = f"arxml/{project_id.lower()}_swc.arxml"
                    
                    if code == "M06":
                        before = "<TYPE-TREF>/AUTOSAR/Platform/ImplementationDataTypes/uint16</TYPE-TREF>"
                        after = "<TYPE-TREF>/AUTOSAR/Platform/ImplementationDataTypes/uint32</TYPE-TREF>"
                        sem = "Datatype width widening from 16-bit to 32-bit"
                    elif code == "M07":
                        before = "<FACTOR>0.1</FACTOR><OFFSET>0</OFFSET>"
                        after = "<FACTOR>0.01</FACTOR><OFFSET>0</OFFSET>"
                        sem = "Physical scaling resolution factor refinement"
                    elif code == "M08":
                        before = f"<VARIABLE-DATA-PROTOTYPE><SHORT-NAME>val_raw</SHORT-NAME></VARIABLE-DATA-PROTOTYPE>"
                        after = f"<VARIABLE-DATA-PROTOTYPE><SHORT-NAME>val_filtered</SHORT-NAME></VARIABLE-DATA-PROTOTYPE>"
                        sem = "Interface data element member alteration"
                    elif code == "M09":
                        before = "<ADMIN-DATA><VERSION>1.0.0</VERSION></ADMIN-DATA>"
                        after = "<ADMIN-DATA><VERSION>2.0.0</VERSION></ADMIN-DATA>"
                        sem = "Interface major version upgrade"
                    else:
                        before = "<SWC-ELEMENT>v1</SWC-ELEMENT>"
                        after = "<SWC-ELEMENT>v2</SWC-ELEMENT>"
                        sem = "ARXML structural update"

                elif art_type == "TEST":
                    t = pick(test_nodes)
                    nid = t["id"]
                    fpath = t.get("file_path", f"tests/test_{project_id.lower()}.json")
                    before = f"TEST_VERIFICATION: {t.get('description', '')} assert expected <= 20"
                    after = f"TEST_VERIFICATION: {t.get('description', '')} assert expected <= 15"
                    sem = "Test expectation assertion updated"

                elif art_type == "DOC":
                    r = pick(req_nodes)
                    nid = r["id"]
                    fpath = "docs/architecture_overview.md"
                    before = "/* Documentation note: System operates under standard conditions. */"
                    after = "/* Documentation note: System operates under standard conditions (reviewed 2026). */"
                    sem = "Pure comment / documentation update without code effect"

                else:  # C_CODE
                    fn = pick(func_nodes)
                    nid = fn["id"]
                    fpath = fn.get("file_path", f"src/{project_id.lower()}_control.c")
                    
                    if code == "M10":
                        before = f"Std_ReturnType {nid}(uint16 raw_input);"
                        after = f"Std_ReturnType {nid}(uint32 raw_input, uint8 flags);"
                        sem = "Function argument and signature change"
                    elif code == "M11":
                        before = f"#define {nid.upper()}_LIMIT 100"
                        after = f"#define {nid.upper()}_LIMIT 75"
                        sem = "C preprocessor threshold constant modification"
                    elif code == "M12":
                        before = f"void {nid}() {{ StepA(); StepB(); }}"
                        after = f"void {nid}() {{ StepA(); StepB(); Step_Validation(); }}"
                        sem = "Added dependency call to validation function"
                    elif code == "M13":
                        before = f"g_status = 1;"
                        after = f"g_filtered_status = 1;"
                        sem = "Modified global state variable write dependency"
                    elif code == "M15":
                        before = f"/* unreferenced local helper */ static void dead_helper() {{ int a = 1; }}"
                        after = f"/* unreferenced local helper */ static void dead_helper() {{ int a = 2; }}"
                        sem = "Modification inside uncalled local dead code"
                    elif code == "M16":
                        before = f"calc_primary();"
                        after = f"calc_primary(); trigger_secondary_safety();"
                        sem = "Indirect dependency branch modification"
                    elif code == "M20":
                        before = f"void {nid}() {{ compute(); send(); }}"
                        after = f"void {nid}() {{ compute_v2(); filter(); send(); }}"
                        sem = "Multiple simultaneous logic and dependency updates"
                    elif code == "M21":
                        before = f"int old_calc_var = 10;"
                        after = f"int new_calc_var = 10; /* renamed */"
                        sem = "Lexical renaming of internal variable"
                    elif code == "M22":
                        before = f"void {nid}_Old() {{ execute(); }}"
                        after = f"void {nid}_New() {{ execute(); }}"
                        sem = "Structural symbol renaming preserving body logic"
                    elif code == "M24":
                        before = f"if (0) {{ execute_unused_routine(); }}"
                        after = f"if (0) {{ execute_unused_routine_v2(); }}"
                        sem = "Dead branch modification"
                    else:
                        before = f"{nid} implementation v1"
                        after = f"{nid} implementation v2"
                        sem = "General C implementation change"

                diff = f"--- {fpath}\n+++ {fpath}\n@@ -1,4 +1,4 @@\n-{before}\n+{after}"

                mutations.append(MutationRecord(
                    mutation_id=m_id,
                    project_id=project_id,
                    change_type=code,
                    category_name=cat_name,
                    source_artifact=fpath,
                    target_node_id=nid,
                    artifact_type=art_type,
                    before_state=before,
                    after_state=after,
                    diff=diff,
                    intended_change_semantics=sem,
                    expected_impact_scope="LOCAL" if code in ["M15", "M24", "M25"] else "PROPAGATED",
                    metadata={"change_type": code, "repeat": repeat + 1}
                ))
                mut_idx += 1

        return mutations
