"""
Synthetic Automotive Multi-Project Generator (v3.0)
Generates 4 coherent, realistic automotive ECU projects:
1. ADAS (Advanced Driver Assistance Systems)
2. Powertrain (Electric Motor & Inverter Control)
3. Battery_EV (Battery Management System & Thermal Control)
4. Body_Electronics (BCM, Lighting, HVAC, Power Window)
Includes rich automotive engineering domain descriptions without data leakage.
"""
import os
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def generate_all_projects():
    base_dir = Path("data/projects")

    # =========================================================================
    # 1. ADAS Project
    # =========================================================================
    adas_dir = base_dir / "adas"
    for sub in ["requirements", "arxml", "src", "tests"]:
        (adas_dir / sub).mkdir(parents=True, exist_ok=True)

    # 1.1 ADAS Requirements
    adas_topics = [
        ("AEB_Deceleration", "Emergency braking deceleration and collision mitigation when obstacle hazard detected.", "ASIL_D"),
        ("ACC_Headway", "Adaptive cruise headway distance tracking and vehicle speed regulation.", "ASIL_B"),
        ("LKA_Steering", "Lane keeping assist steering torque regulation and lane departure avoidance.", "ASIL_B"),
        ("Sensor_Radar", "Long-range radar object distance measurement and relative velocity tracking.", "ASIL_D"),
        ("Sensor_Camera", "Front camera vision object detection and pedestrian path prediction.", "ASIL_D"),
        ("Actuator_Brake", "Hydraulic brake pressure hold and electronic stability brake intervention.", "ASIL_D"),
        ("Driver_Alert", "Audio and visual collision warning indication upon time-to-collision threshold.", "ASIL_B"),
    ]

    adas_reqs = []
    r_id = 1
    for topic, desc, asil in adas_topics:
        for i in range(1, 9):
            adas_reqs.append({
                "id": f"REQ_ADAS_{r_id:03d}",
                "name": f"{topic}_Req_{i:02d}",
                "description": f"{desc} Operational verification requirement variant {i}.",
                "asil_level": asil,
                "project": "ADAS",
                "verification_tests": [f"TC_ADAS_{r_id:03d}"]
            })
            r_id += 1

    with open(adas_dir / "requirements" / "adas_requirements.json", "w", encoding="utf-8") as f:
        json.dump(adas_reqs, f, indent=2)

    # 1.2 ADAS ARXML & SWCs
    swc_names_adas = ["SWC_AEB", "SWC_ACC", "SWC_LKA", "SWC_Radar", "SWC_Camera", "SWC_BrakeCtrl", "SWC_Fusion", "SWC_Warning", "SWC_DriverInput", "SWC_Actuation"]
    for swc in swc_names_adas:
        arxml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>ADAS_Components</SHORT-NAME>
      <ELEMENTS>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>{swc}</SHORT-NAME>
          <DESC>AUTOSAR Application SWC {swc} for ADAS control</DESC>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>P_{swc}_Command</SHORT-NAME>
              <PROVIDED-INTERFACE-TREF>/Interfaces/I_{swc}_Out</PROVIDED-INTERFACE-TREF>
            </P-PORT-PROTOTYPE>
            <R-PORT-PROTOTYPE>
              <SHORT-NAME>R_{swc}_SensorInput</SHORT-NAME>
              <REQUIRED-INTERFACE-TREF>/Interfaces/I_{swc}_In</REQUIRED-INTERFACE-TREF>
            </R-PORT-PROTOTYPE>
          </PORTS>
          <SWC-INTERNAL-BEHAVIOR>
            <SHORT-NAME>{swc}_Behavior</SHORT-NAME>
            <RUNNABLES>
              <RUNNABLE-ENTITY>
                <SHORT-NAME>RE_{swc}_Step</SHORT-NAME>
                <SYMBOL>{swc}_Step</SYMBOL>
              </RUNNABLE-ENTITY>
            </RUNNABLES>
          </SWC-INTERNAL-BEHAVIOR>
        </APPLICATION-SW-COMPONENT-TYPE>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>
"""
        with open(adas_dir / "arxml" / f"{swc}.arxml", "w", encoding="utf-8") as f:
            f.write(arxml_content)

    # 1.3 ADAS C Functions
    c_lines_adas = ['#include "Std_Types.h"', '']
    domain_descs_adas = [
        "Emergency braking deceleration command and autonomous collision avoidance stopping execution.",
        "Adaptive cruise headway gap regulation and longitudinal velocity tracking.",
        "Lane departure warning and lateral steering torque assist regulation.",
        "Radar proximity distance processing and relative obstacle velocity calculation.",
        "Camera computer vision object classification and roadway path estimation.",
        "Hydraulic braking pressure actuator command and electronic stability intervention.",
        "Driver auditory collision alert and visual instrument cluster warning.",
        "Sensor fusion multi-target state estimation and track association confidence.",
        "Driver pedal override detection and steering wheel hands-on sensing.",
        "Brake actuator deceleration force modulation and vehicle standstill hold."
    ]

    for i in range(1, 86):
        fn_name = f"ADAS_Func_{i:03d}"
        topic_desc = domain_descs_adas[(i - 1) % len(domain_descs_adas)]
        swc_owner = swc_names_adas[(i - 1) % len(swc_names_adas)]
        callee = f"ADAS_Func_{(i % 85) + 1:03d}"
        c_lines_adas.extend([
            f"/**",
            f" * @brief {fn_name}: {topic_desc}",
            f" */",
            f"Std_ReturnType {fn_name}(uint32 input_val) {{",
            f"    Rte_Read_Sensor(input_val);",
            f"    if (input_val < 50) {{",
            f"        {callee}(input_val + 1);",
            f"    }}",
            f"    Rte_Write_{swc_owner}_Signal(input_val);",
            f"    return 0;",
            f"}}",
            ""
        ])

    with open(adas_dir / "src" / "adas_controller.c", "w", encoding="utf-8") as f:
        f.write("\n".join(c_lines_adas))

    # 1.4 ADAS Tests
    adas_tests = []
    for i in range(1, 86):
        topic_desc = domain_descs_adas[(i - 1) % len(domain_descs_adas)]
        is_safe = (i <= 25)
        adas_tests.append({
            "id": f"TC_ADAS_{i:03d}",
            "name": f"Test_ADAS_Function_{i:03d}",
            "target_function": f"ADAS_Func_{i:03d}",
            "target_swc": swc_names_adas[(i - 1) % len(swc_names_adas)],
            "requirement_id": f"REQ_ADAS_{min(r_id-1, i):03d}",
            "safety_level": "ASIL_D" if is_safe else "QM",
            "description": f"Verification test for {topic_desc}."
        })

    with open(adas_dir / "tests" / "adas_tests.json", "w", encoding="utf-8") as f:
        json.dump(adas_tests, f, indent=2)

    # =========================================================================
    # 2. Powertrain Project
    # =========================================================================
    pt_dir = base_dir / "powertrain"
    for sub in ["requirements", "arxml", "src", "tests"]:
        (pt_dir / sub).mkdir(parents=True, exist_ok=True)

    pt_descs = [
        "Electric motor stator magnetic field torque regulation and PMSM field oriented control.",
        "Inverter IGBT temperature thermal protection and power derating control.",
        "Accelerator pedal demand torque mapping and traction torque ramp rate limitation.",
        "Regenerative braking energy recovery and deceleration torque blending.",
        "High voltage DC bus voltage regulation and active discharge fail-safe.",
        "Motor rotor angular position resolver sensor decoding and speed estimation.",
        "Traction motor over-speed protection and emergency torque shutoff."
    ]

    pt_reqs = []
    for i in range(1, 51):
        desc = pt_descs[(i - 1) % len(pt_descs)]
        pt_reqs.append({
            "id": f"REQ_PT_{i:03d}",
            "name": f"PT_Req_{i:02d}",
            "description": f"{desc} Parameter verification variant {i}.",
            "asil_level": "ASIL_D" if i <= 20 else "QM",
            "project": "POWERTRAIN",
            "verification_tests": [f"TC_PT_{i:03d}"]
        })
    with open(pt_dir / "requirements" / "pt_requirements.json", "w", encoding="utf-8") as f:
        json.dump(pt_reqs, f, indent=2)

    c_lines_pt = ['#include "Std_Types.h"', '']
    for i in range(1, 81):
        fn_name = f"PT_Func_{i:03d}"
        desc = pt_descs[(i - 1) % len(pt_descs)]
        callee = f"PT_Func_{(i % 80) + 1:03d}"
        c_lines_pt.extend([
            f"/**",
            f" * @brief {fn_name}: {desc}",
            f" */",
            f"Std_ReturnType {fn_name}(uint32 input_val) {{",
            f"    Rte_Read_Sensor(input_val);",
            f"    if (input_val > 100) {{ {callee}(input_val - 1); }}",
            f"    Rte_Write_Actuator(input_val);",
            f"    return 0;",
            f"}}",
            ""
        ])
    with open(pt_dir / "src" / "powertrain_controller.c", "w", encoding="utf-8") as f:
        f.write("\n".join(c_lines_pt))

    pt_tests = []
    for i in range(1, 81):
        desc = pt_descs[(i - 1) % len(pt_descs)]
        pt_tests.append({
            "id": f"TC_PT_{i:03d}",
            "name": f"Test_PT_{i:03d}",
            "target_function": f"PT_Func_{i:03d}",
            "target_swc": "SWC_MotorControl",
            "requirement_id": f"REQ_PT_{min(50, i):03d}",
            "safety_level": "ASIL_D" if i <= 25 else "QM",
            "description": f"Verification test for {desc}."
        })
    with open(pt_dir / "tests" / "pt_tests.json", "w", encoding="utf-8") as f:
        json.dump(pt_tests, f, indent=2)

    # =========================================================================
    # 3. Battery_EV Project
    # =========================================================================
    bms_dir = base_dir / "battery_ev"
    for sub in ["requirements", "arxml", "src", "tests"]:
        (bms_dir / sub).mkdir(parents=True, exist_ok=True)

    bms_descs = [
        "Battery cell charging rate regulation and pack thermal protection derate mode.",
        "High-voltage DC contactor isolation interlock and emergency disconnect.",
        "Battery state of charge (SoC) estimation and cell balancing algorithm.",
        "Accumulator pack sub-zero ambient temperature heating loop management.",
        "Battery over-voltage and thermal runaway detection alarm protocol.",
        "Insulation resistance monitoring and chassis ground fault detection."
    ]

    bms_reqs = []
    for i in range(1, 51):
        desc = bms_descs[(i - 1) % len(bms_descs)]
        bms_reqs.append({
            "id": f"REQ_BMS_{i:03d}",
            "name": f"BMS_Req_{i:02d}",
            "description": f"{desc} Operational verification requirement {i}.",
            "asil_level": "ASIL_D" if i <= 20 else "QM",
            "project": "BATTERY_EV",
            "verification_tests": [f"TC_BMS_{i:03d}"]
        })
    with open(bms_dir / "requirements" / "bms_requirements.json", "w", encoding="utf-8") as f:
        json.dump(bms_reqs, f, indent=2)

    c_lines_bms = ['#include "Std_Types.h"', '']
    for i in range(1, 81):
        fn_name = f"BMS_Func_{i:03d}"
        desc = bms_descs[(i - 1) % len(bms_descs)]
        callee = f"BMS_Func_{(i % 80) + 1:03d}"
        c_lines_bms.extend([
            f"/**",
            f" * @brief {fn_name}: {desc}",
            f" */",
            f"Std_ReturnType {fn_name}(uint32 input_val) {{",
            f"    Rte_Read_Sensor(input_val);",
            f"    if (input_val > 100) {{ {callee}(input_val - 1); }}",
            f"    Rte_Write_Actuator(input_val);",
            f"    return 0;",
            f"}}",
            ""
        ])
    with open(bms_dir / "src" / "bms_controller.c", "w", encoding="utf-8") as f:
        f.write("\n".join(c_lines_bms))

    bms_tests = []
    for i in range(1, 81):
        desc = bms_descs[(i - 1) % len(bms_descs)]
        bms_tests.append({
            "id": f"TC_BMS_{i:03d}",
            "name": f"Test_BMS_{i:03d}",
            "target_function": f"BMS_Func_{i:03d}",
            "target_swc": "SWC_BMS_CellSupervisor",
            "requirement_id": f"REQ_BMS_{min(50, i):03d}",
            "safety_level": "ASIL_D" if i <= 25 else "QM",
            "description": f"Verification test for {desc}."
        })
    with open(bms_dir / "tests" / "bms_tests.json", "w", encoding="utf-8") as f:
        json.dump(bms_tests, f, indent=2)

    # 4. Generate Body Electronics
    from scripts.generate_body_project import generate_body_electronics_project
    generate_body_electronics_project()

    print("[OK] Generated all 4 projects with rich domain descriptions.")


if __name__ == "__main__":
    generate_all_projects()
