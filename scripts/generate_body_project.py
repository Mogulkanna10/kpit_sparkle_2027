"""
Generator for Body Electronics Subsystem (Lighting, Door/Window, BCM, Climate, Immobilizer)
Adds 4th project to benchmark environment.
"""
import os
import json
from pathlib import Path


def generate_body_electronics_project():
    base_dir = Path("data/projects/body_electronics")
    (base_dir / "requirements").mkdir(parents=True, exist_ok=True)
    (base_dir / "arxml").mkdir(parents=True, exist_ok=True)
    (base_dir / "src").mkdir(parents=True, exist_ok=True)
    (base_dir / "tests").mkdir(parents=True, exist_ok=True)

    # 1. Requirements
    reqs = []
    body_topics = [
        ("BCM_Lighting", "Exterior and interior lighting automation based on ambient illumination and door switches.", "ASIL_B"),
        ("BCM_DoorLock", "Central door locking, auto-relock safety interlocks, and crash unlock triggers.", "ASIL_B"),
        ("BCM_Wiper", "Rain-sensing windshield wiper interval and high-speed wipe regulation.", "QM"),
        ("HVAC_CabinComfort", "Cabin temperature closed-loop regulation and blower motor power management.", "QM"),
        ("BCM_Immobilizer", "Cryptographic key challenge-response and passive start authentication.", "ASIL_C"),
        ("BCM_PowerWindow", "Anti-pinch obstacle detection and one-touch power window express close.", "ASIL_B")
    ]

    req_idx = 1
    for topic, desc, asil in body_topics:
        for i in range(1, 9):
            reqs.append({
                "id": f"REQ_BODY_{req_idx:03d}",
                "name": f"{topic}_Req_{i:02d}",
                "description": f"{desc} [Parameter verification variant {i}].",
                "asil_level": asil,
                "project": "BODY_ELECTRONICS",
                "verification_tests": [f"TC_BODY_{req_idx:03d}"]
            })
            req_idx += 1

    with open(base_dir / "requirements" / "body_requirements.json", "w", encoding="utf-8") as f:
        json.dump(reqs, f, indent=2)

    # 2. ARXML
    arxml_content = """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>Body_Components</SHORT-NAME>
      <ELEMENTS>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>SWC_BCM_Lighting</SHORT-NAME>
          <DESC>Body Control Module Lighting Controller</DESC>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>P_HeadlampCmd</SHORT-NAME>
              <PROVIDED-INTERFACE-TREF>/Interfaces/I_LightControl</PROVIDED-INTERFACE-TREF>
            </P-PORT-PROTOTYPE>
            <R-PORT-PROTOTYPE>
              <SHORT-NAME>R_AmbientLight</SHORT-NAME>
              <REQUIRED-INTERFACE-TREF>/Interfaces/I_SensorData</REQUIRED-INTERFACE-TREF>
            </R-PORT-PROTOTYPE>
          </PORTS>
          <SWC-INTERNAL-BEHAVIOR>
            <SHORT-NAME>SWC_BCM_Lighting_Behavior</SHORT-NAME>
            <RUNNABLES>
              <RUNNABLE-ENTITY>
                <SHORT-NAME>RE_BCM_Lighting_Step</SHORT-NAME>
                <SYMBOL>BCM_Lighting_Step</SYMBOL>
              </RUNNABLE-ENTITY>
            </RUNNABLES>
          </SWC-INTERNAL-BEHAVIOR>
        </APPLICATION-SW-COMPONENT-TYPE>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>SWC_HVAC_Controller</SHORT-NAME>
          <DESC>Cabin HVAC and Climate Controller</DESC>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>P_BlowerPower</SHORT-NAME>
              <PROVIDED-INTERFACE-TREF>/Interfaces/I_HVACControl</PROVIDED-INTERFACE-TREF>
            </P-PORT-PROTOTYPE>
          </PORTS>
          <SWC-INTERNAL-BEHAVIOR>
            <SHORT-NAME>SWC_HVAC_Behavior</SHORT-NAME>
            <RUNNABLES>
              <RUNNABLE-ENTITY>
                <SHORT-NAME>RE_HVAC_Step</SHORT-NAME>
                <SYMBOL>HVAC_Step</SYMBOL>
              </RUNNABLE-ENTITY>
            </RUNNABLES>
          </SWC-INTERNAL-BEHAVIOR>
        </APPLICATION-SW-COMPONENT-TYPE>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>
"""
    with open(base_dir / "arxml" / "SWC_Body.arxml", "w", encoding="utf-8") as f:
        f.write(arxml_content)

    # 3. C Source Code
    c_lines = [
        '#include "Rte_Body.h"',
        '#include "Std_Types.h"',
        '',
        '/* Body Control Module Implementation */',
        'static uint8 g_cabin_target_temp = 22;',
        'static uint8 g_ambient_lux = 100;',
        ''
    ]

    for i in range(1, 49):
        fn_name = f"BODY_Func_{i:03d}"
        c_lines.extend([
            f"/**",
            f" * @brief Body controller sub-function {fn_name}",
            f" */",
            f"Std_ReturnType {fn_name}(uint32 input_data) {{",
            f"    Rte_Read_Sensor(input_data);",
            f"    if (input_data > 100) {{",
            f"        BODY_Func_{(i % 48) + 1:03d}(input_data - 1);",
            f"    }}",
            f"    Rte_Write_Actuator(input_data);",
            f"    return E_OK;",
            f"}}",
            ""
        ])

    with open(base_dir / "src" / "body_controller.c", "w", encoding="utf-8") as f:
        f.write("\n".join(c_lines))

    # 4. Tests
    tests = []
    for i in range(1, 49):
        is_safe = (i <= 16)  # First 16 are safety-critical (ASIL B / C)
        tests.append({
            "id": f"TC_BODY_{i:03d}",
            "name": f"Test_Body_Functionality_{i:03d}",
            "target_function": f"BODY_Func_{i:03d}",
            "target_swc": "SWC_BCM_Lighting" if i % 2 == 0 else "SWC_HVAC_Controller",
            "requirement_id": f"REQ_BODY_{i:03d}",
            "safety_level": "ASIL_B" if is_safe else "QM",
            "description": f"Verification test for body electronic sub-function {i:03d}."
        })

    with open(base_dir / "tests" / "body_tests.json", "w", encoding="utf-8") as f:
        json.dump(tests, f, indent=2)

    print("[OK] Generated Body Electronics project (48 reqs, 48 C functions, 48 tests)")


if __name__ == "__main__":
    generate_body_electronics_project()
