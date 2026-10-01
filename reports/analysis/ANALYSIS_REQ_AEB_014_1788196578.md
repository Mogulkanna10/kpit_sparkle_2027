# AURA-Impact Analysis Report: `REQ_AEB_014`
- **Analysis ID:** ANALYSIS_REQ_AEB_014_1788196578
- **Timestamp:** 2026-08-31T22:46:18.451432
- **Subsystem:** ADAS

## Summary Metrics
- **Structural Impacts:** 0
- **Semantic Recoveries:** 3
- **Review Required Items:** 0
- **Total Impacted Artifacts:** 3
- **Selected Tests:** 2 / 4 (50.0% reduction)
- **Safety-Critical Tests Retained:** 2
- **Online Latency:** 0.73 ms

## Impacted Engineering Artifacts
| Artifact ID | Type | Stage | Confidence | Reason |
| :--- | :--- | :--- | :--- | :--- |
| `C_Function_TriggerBrake` | C_Function | **SEMANTIC** | 0.73 | Semantic similarity (0.73) above threshold with verified context. |
| `REQ_AEB_001` | Requirement | **SEMANTIC** | 0.61 | Semantic similarity (0.61) above threshold with verified context. |
| `C_Function_CalculateTTC` | C_Function | **SEMANTIC** | 0.50 | Semantic similarity (0.50) above threshold with verified context. |

## Selected Regression Test Cases
| Test ID | Description | Safety Class | Source |
| :--- | :--- | :--- | :--- |
| `TC_AEB_002` | Verify Emergency Brake Actuation deceleration ramp and hydraulic pressure clamping. | **ASIL_D** | EXPLICIT_TRACE |
| `TC_AEB_001` | Verify Time-To-Collision calculation accuracy under varied radar distance profiles. | **ASIL_D** | EXPLICIT_TRACE |