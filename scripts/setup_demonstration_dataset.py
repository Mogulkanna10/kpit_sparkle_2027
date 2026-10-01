"""
Sets up the synthetic demonstration dataset for KPIT Sparkle Round 2.
Clearly labeled as a DEMONSTRATION DATASET. Not proprietary OEM data.
"""
import os
import json
from pathlib import Path

def setup():
    base_dir = Path("data/demonstration_dataset")
    for sub in ["requirements", "arxml", "src", "tests", "scenarios"]:
        (base_dir / sub).mkdir(parents=True, exist_ok=True)

    # 1. README.md
    readme = """# DEMONSTRATION DATASET (SYNTHETIC)
## KPIT Sparkle 2027 Round 2 — AURA-Impact Engineering Demonstrator

> **DISCLAIMER:** This dataset is a **synthetic engineering demonstration project** created strictly for evaluating and demonstrating the AURA-Impact change-impact analysis engine. It does **NOT** contain proprietary OEM or Tier-1 software.

### Subsystem Topology
- **ADAS Subsystem (ECU_1, ASIL-D):** Autonomous Emergency Braking (AEB), Radar processing, Time-to-Collision (TTC) calculation, emergency hydraulic deceleration clamping.
- **Body Electronics (ECU_Body, QM):** Cabin climate defroster, blower power level, interior comfort (includes semantic decoy with overlapping terminology).
- **Powertrain (ECU_Engine, ASIL-B/C):** Adaptive Cruise Control (ACC) target velocity modulation.
- **Regression Suite:** 100 structured test cases across ASIL-D, ASIL-B, and QM safety classes.
"""
    with open(base_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    # 2. requirements/reqs.json
    reqs = [
        {
            "id": "REQ_AEB_001",
            "title": "Autonomous Emergency Braking Time-to-Collision Calculation",
            "description": "The AEB controller shall compute Time-to-Collision (TTC) based on radar distance and ego vehicle velocity.",
            "subsystem": "ADAS",
            "ecu": "ECU_1",
            "asil": "ASIL_D",
            "trace_links": ["SWC_AEB"]
        },
        {
            "id": "REQ_AEB_014",
            "title": "Emergency Braking Actuation Deceleration Clamp",
            "description": "Trigger emergency deceleration and clamp hydraulic brake line pressure when TTC falls below threshold.",
            "subsystem": "ADAS",
            "ecu": "ECU_1",
            "asil": "ASIL_D",
            "trace_links": []
        },
        {
            "id": "REQ_BODY_005",
            "title": "Cabin Temperature Climate Defroster Blower Control",
            "description": "Adjust cabin temperature and defroster blower power level for interior passenger comfort.",
            "subsystem": "Body_Electronics",
            "ecu": "ECU_Body",
            "asil": "QM",
            "trace_links": ["SWC_BodyControl"]
        },
        {
            "id": "REQ_AMB_099",
            "title": "Unspecified Driver Warning Alert",
            "description": "Provide ambiguous driver notification when alert conditions occur without clear timing or threshold parameters.",
            "subsystem": "ADAS",
            "ecu": "ECU_1",
            "asil": "ASIL_B",
            "trace_links": []
        },
        {
            "id": "REQ_ACC_001",
            "title": "Adaptive Cruise Control Speed Target",
            "description": "Maintain vehicle cruise setpoint speed and throttle modulation according to forward clearance.",
            "subsystem": "Powertrain",
            "ecu": "ECU_Engine",
            "asil": "ASIL_B",
            "trace_links": ["SWC_ACC"]
        }
    ]
    with open(base_dir / "requirements" / "reqs.json", "w", encoding="utf-8") as f:
        json.dump(reqs, f, indent=2)

    # 3. arxml/demonstration_swc.arxml
    arxml_content = """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>Demo_Components</SHORT-NAME>
      <ELEMENTS>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>SWC_AEB</SHORT-NAME>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>PpBrakeCommand</SHORT-NAME>
              <PROVIDED-INTERFACE-TREF>/Interfaces/If_BrakeCommand</PROVIDED-INTERFACE-TREF>
            </P-PORT-PROTOTYPE>
            <R-PORT-PROTOTYPE>
              <SHORT-NAME>RpRadarTarget</SHORT-NAME>
              <REQUIRED-INTERFACE-TREF>/Interfaces/If_RadarTarget</REQUIRED-INTERFACE-TREF>
            </R-PORT-PROTOTYPE>
          </PORTS>
          <INTERNAL-BEHAVIORS>
            <SWC-INTERNAL-BEHAVIOR>
              <SHORT-NAME>IB_SWC_AEB</SHORT-NAME>
              <RUNNABLES>
                <RUNNABLE-ENTITY>
                  <SHORT-NAME>Runnable_AEB</SHORT-NAME>
                  <SYMBOL>C_Function_CalculateTTC</SYMBOL>
                </RUNNABLE-ENTITY>
              </RUNNABLES>
            </SWC-INTERNAL-BEHAVIOR>
          </INTERNAL-BEHAVIORS>
        </APPLICATION-SW-COMPONENT-TYPE>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>SWC_BodyControl</SHORT-NAME>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>PpClimateCommand</SHORT-NAME>
              <PROVIDED-INTERFACE-TREF>/Interfaces/If_ClimateCommand</PROVIDED-INTERFACE-TREF>
            </P-PORT-PROTOTYPE>
          </PORTS>
          <INTERNAL-BEHAVIORS>
            <SWC-INTERNAL-BEHAVIOR>
              <SHORT-NAME>IB_SWC_BodyControl</SHORT-NAME>
              <RUNNABLES>
                <RUNNABLE-ENTITY>
                  <SHORT-NAME>Runnable_Climate</SHORT-NAME>
                  <SYMBOL>C_Function_CabinClimateControl</SYMBOL>
                </RUNNABLE-ENTITY>
              </RUNNABLES>
            </SWC-INTERNAL-BEHAVIOR>
          </INTERNAL-BEHAVIORS>
        </APPLICATION-SW-COMPONENT-TYPE>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>SWC_ACC</SHORT-NAME>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>PpSpeedTarget</SHORT-NAME>
              <PROVIDED-INTERFACE-TREF>/Interfaces/If_SpeedTarget</PROVIDED-INTERFACE-TREF>
            </P-PORT-PROTOTYPE>
          </PORTS>
          <INTERNAL-BEHAVIORS>
            <SWC-INTERNAL-BEHAVIOR>
              <SHORT-NAME>IB_SWC_ACC</SHORT-NAME>
              <RUNNABLES>
                <RUNNABLE-ENTITY>
                  <SHORT-NAME>Runnable_ACC</SHORT-NAME>
                  <SYMBOL>C_Function_AdaptiveCruiseSpeed</SYMBOL>
                </RUNNABLE-ENTITY>
              </RUNNABLES>
            </SWC-INTERNAL-BEHAVIOR>
          </INTERNAL-BEHAVIORS>
        </APPLICATION-SW-COMPONENT-TYPE>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>"""
    with open(base_dir / "arxml" / "demonstration_swc.arxml", "w", encoding="utf-8") as f:
        f.write(arxml_content)

    # 4. src/aeb_controller.c
    c_content = """#include <stdio.h>
#include <stdbool.h>

/* AUTOSAR AEB C Implementation */

void C_Function_CalculateTTC(float distance, float relative_speed) {
    if (relative_speed > 0.0f) {
        float ttc = distance / relative_speed;
        if (ttc < 1.5f) {
            C_Function_TriggerBrake(ttc);
        }
    }
}

void C_Function_TriggerBrake(float ttc_value) {
    /* Emergency Deceleration Actuation Clamp - Hidden Semantic Target */
    printf("EMERGENCY BRAKE TRIGGERED: TTC=%f\\n", ttc_value);
    Rte_Write_PpBrakeCommand_DecelRequest(8.5f);
}

void C_Function_CabinClimateControl(float target_temp) {
    /* Body Electronics Decoy Function */
    printf("Setting cabin temperature and defroster blower to %f\\n", target_temp);
}

void C_Function_UnspecifiedAlert(int alert_code) {
    /* Ambiguous alert function */
    printf("Driver alert code: %d\\n", alert_code);
}

void C_Function_AdaptiveCruiseSpeed(float desired_speed) {
    /* Powertrain ACC function */
    printf("ACC setpoint velocity: %f km/h\\n", desired_speed);
}
"""
    with open(base_dir / "src" / "aeb_controller.c", "w", encoding="utf-8") as f:
        f.write(c_content)

    # 5. tests/test_suite.json (100 tests)
    tests = [
        {
            "id": "TC_AEB_001",
            "description": "Verify Time-To-Collision calculation accuracy under varied radar distance profiles.",
            "artifact_targets": ["C_Function_CalculateTTC", "SWC_AEB", "REQ_AEB_001"],
            "safety_class": "ASIL_D",
            "subsystem": "ADAS",
            "ecu": "ECU_1"
        },
        {
            "id": "TC_AEB_002",
            "description": "Verify Emergency Brake Actuation deceleration ramp and hydraulic pressure clamping.",
            "artifact_targets": ["C_Function_TriggerBrake"],
            "safety_class": "ASIL_D",
            "subsystem": "ADAS",
            "ecu": "ECU_1"
        },
        {
            "id": "TC_BODY_001",
            "description": "Verify Cabin Climate blower level and setpoint stabilization.",
            "artifact_targets": ["C_Function_CabinClimateControl", "REQ_BODY_005", "SWC_BodyControl"],
            "safety_class": "QM",
            "subsystem": "Body_Electronics",
            "ecu": "ECU_Body"
        },
        {
            "id": "TC_AMB_001",
            "description": "Verify driver alert chime buzzer triggering.",
            "artifact_targets": ["C_Function_UnspecifiedAlert"],
            "safety_class": "ASIL_B",
            "subsystem": "ADAS",
            "ecu": "ECU_1"
        },
        {
            "id": "TC_ACC_001",
            "description": "Verify Adaptive Cruise Control throttle modulation and vehicle velocity tracking.",
            "artifact_targets": ["C_Function_AdaptiveCruiseSpeed", "REQ_ACC_001", "SWC_ACC"],
            "safety_class": "ASIL_B",
            "subsystem": "Powertrain",
            "ecu": "ECU_Engine"
        }
    ]

    subsystems = ["Body_Electronics", "Chassis", "Infotainment", "Powertrain", "Comfort", "Thermal"]
    for i in range(1, 96):
        sub = subsystems[i % len(subsystems)]
        asil = "ASIL_B" if i % 10 == 0 else "QM"
        tests.append({
            "id": f"TC_REG_{i:03d}",
            "description": f"Regression baseline verification for component block #{i} in {sub}.",
            "artifact_targets": [f"SWC_Baseline_{sub}_{i:03d}"],
            "safety_class": asil,
            "subsystem": sub,
            "ecu": f"ECU_{sub}"
        })

    with open(base_dir / "tests" / "test_suite.json", "w", encoding="utf-8") as f:
        json.dump(tests, f, indent=2)

    # 6. Predefined Scenarios
    scenarios = {
        "1_explicit_structural.json": {
            "name": "Explicit Structural Impact",
            "description": "Change in REQ_AEB_001 propagates deterministically through SWC_AEB to C_Function_CalculateTTC.",
            "artifact_id": "REQ_AEB_001",
            "artifact_type": "Requirement",
            "subsystem": "ADAS",
            "ecu": "ECU_1",
            "change_type": "MODIFY",
            "after_content": "Update Time-to-Collision threshold formula to account for wet asphalt friction coefficient.",
            "change_semantics": "Time-to-collision calculation TTC radar distance ego speed",
            "expected": {
                "structural_count": 3,
                "semantic_count": 0,
                "retained_safety_tests": ["TC_AEB_001"]
            }
        },
        "2_hidden_semantic.json": {
            "name": "Graph-Blind Hidden Semantic Dependency",
            "description": "Change in REQ_AEB_014 has NO explicit trace links, but latent semantic dependency on C_Function_TriggerBrake is recovered.",
            "artifact_id": "REQ_AEB_014",
            "artifact_type": "Requirement",
            "subsystem": "ADAS",
            "ecu": "ECU_1",
            "change_type": "MODIFY",
            "after_content": "Emergency braking actuation and deceleration pressure clamping on obstacle arrival.",
            "change_semantics": "Emergency deceleration brake trigger clamp hydraulic braking hazard",
            "force_semantic": True,
            "expected": {
                "graph_found": 0,
                "semantic_recovered": 1,
                "recovered_artifact": "C_Function_TriggerBrake",
                "retained_safety_tests": ["TC_AEB_002"]
            }
        },
        "3_semantic_decoy.json": {
            "name": "Semantic Decoy Rejection",
            "description": "Semantic search on brake trigger pressure matches C_Function_TriggerBrake (ADAS) and C_Function_CabinClimateControl (Body). ContextFilter rejects Body decoy.",
            "artifact_id": "REQ_AEB_014",
            "artifact_type": "Requirement",
            "subsystem": "ADAS",
            "ecu": "ECU_1",
            "change_type": "MODIFY",
            "after_content": "Emergency braking actuation and deceleration pressure clamping on obstacle arrival.",
            "change_semantics": "Emergency deceleration brake trigger clamp hydraulic braking hazard pressure blower level",
            "filter_subsystem_in_index": False,
            "force_semantic": True,
            "expected": {
                "accepted": ["C_Function_TriggerBrake"],
                "rejected_decoys": ["C_Function_CabinClimateControl"],
                "rejection_reason": "Subsystem mismatch"
            }
        },
        "4_ambiguous_change.json": {
            "name": "Ambiguous Change (Review Required)",
            "description": "Under-specified requirement REQ_AMB_099 lacks technical parameters, triggering REVIEW_REQUIRED instead of hallucinating certainty.",
            "artifact_id": "REQ_AMB_099",
            "artifact_type": "Requirement",
            "subsystem": "ADAS",
            "ecu": "ECU_1",
            "change_type": "MODIFY",
            "after_content": "Under-specified driver notification logic with ambiguous alert thresholds.",
            "change_semantics": "Ambiguous unclear driver alert notification without technical parameters",
            "force_semantic": True,
            "expected": {
                "status": "REVIEW_REQUIRED"
            }
        },
        "5_safety_critical.json": {
            "name": "Safety-Critical Regression (Non-Bypassable Gate)",
            "description": "Simulate removal attempt of mandatory ASIL-D safety tests TC_AEB_001 and TC_AEB_002. Safety Gate blocks exclusion.",
            "artifact_id": "REQ_AEB_001",
            "artifact_type": "Requirement",
            "subsystem": "ADAS",
            "ecu": "ECU_1",
            "change_type": "MODIFY",
            "after_content": "Update Time-to-Collision threshold formula.",
            "change_semantics": "Time-to-collision calculation TTC radar distance",
            "mandatory_safety_tests": ["TC_AEB_001", "TC_AEB_002"],
            "expected": {
                "safety_invariant": "100% Retained",
                "blocked_attempt": True
            }
        },
        "6_suite_reduction.json": {
            "name": "Large Regression Suite Reduction",
            "description": "Starting with 100 regression tests, localized change in REQ_AEB_001 selects only required verification tests (96% suite reduction).",
            "artifact_id": "REQ_AEB_001",
            "artifact_type": "Requirement",
            "subsystem": "ADAS",
            "ecu": "ECU_1",
            "change_type": "MODIFY",
            "after_content": "Update Time-to-Collision threshold formula.",
            "change_semantics": "Time-to-collision calculation TTC radar distance",
            "expected": {
                "total_tests": 100,
                "selected_tests_max": 5,
                "reduction_pct_min": 95.0
            }
        }
    }

    for fname, sdata in scenarios.items():
        with open(base_dir / "scenarios" / fname, "w", encoding="utf-8") as f:
            json.dump(sdata, f, indent=2)

    print(f"Created demonstration dataset successfully in {base_dir} with 100 tests and 6 scenarios.")

if __name__ == "__main__":
    setup()
