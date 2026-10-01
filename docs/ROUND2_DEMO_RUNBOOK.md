# AURA-IMPACT ROUND 2 DEMONSTRATOR RUNBOOK

**Document Reference:** `docs/ROUND2_DEMO_RUNBOOK.md`  
**Purpose:** Comprehensive guide for judges and engineers to run, inspect, and validate the AURA-Impact Round 2 engineering demonstrator.

---

## 1. Quick Start (One-Command Operations)

### Launch Demonstration Dashboard
```bash
python -m streamlit run dashboard/app.py
```
*Access the interactive interface at: `http://localhost:8501`*

### Run Full Round 2 Automated Validation (12 Scenarios)
```bash
python scripts/run_round2_validation.py
```
*Executes all 12 validation scenarios, records performance latencies, logs adversarial failure analyses, and summarizes results.*

### Run Complete Test Suite (252 Tests)
```bash
python -m pytest tests/ -q
```
*Verifies all 220 core baseline tests and 32 Round 2 demonstrator tests.*

---

## 2. Environment Setup & Dependencies

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14.
- Windows, Linux, or macOS.

### Installation
Ensure standard project dependencies are installed in your active virtual environment:
```bash
pip install -r requirements.txt
```

Key runtime dependencies:
- `streamlit`: Interactive demonstration web interface.
- `networkx`: Deterministic graph modeling and bounded traversal.
- `numpy`: Fast vectorized matrix calculations.
- `pytest`: Automated test execution.

*Note: No GPU, external LLM, cloud API keys, or proprietary licenses are required. AURA-Impact runs 100% locally and offline.*

---

## 3. Demonstration Dataset Setup

The demonstration dataset is located in:
```
data/demonstration_dataset/
├── reqs.json                 # Requirements tagged with ASIL, ECU, Subsystem
├── demonstration_swc.arxml   # AUTOSAR XML SWC descriptions and ports
├── aeb_controller.c          # C implementation source (ADAS)
├── body_controller.c         # C implementation source (Body Electronics)
├── test_suite.json           # 100 verification test cases
└── scenarios/                # Pre-packaged 1-click test scenarios
    ├── scenario_01_structural.json
    ├── scenario_02_hidden_semantic.json
    ├── scenario_03_decoy_rejection.json
    ├── scenario_04_ambiguity.json
    ├── scenario_05_safety_gate.json
    └── scenario_06_large_reduction.json
```

All data in this folder is explicitly labeled **SYNTHETIC DEMONSTRATION DATASET** designed to demonstrate automotive AUTOSAR integration workflows. It is completely isolated from the research benchmark dataset.

---

## 4. How to Launch and Use the Dashboard

1. Start the Streamlit application:
   ```bash
   python -m streamlit run dashboard/app.py
   ```
2. In your web browser, navigate to: `http://localhost:8501`.
3. In the left sidebar:
   - **Dataset Source:** Select `"Synthetic Demonstration Dataset (data/demonstration_dataset)"`.
   - **Click:** `"Load / Refresh Dataset"`.
   - **Demo Scenarios:** Choose any scenario (e.g., `SCENARIO_02: Hidden Semantic Dependency`).
   - **Click:** `"Run Impact Analysis"`.

4. Explore the 6 dedicated analysis tabs:
   - **Tab 1: Executive Summary:** View impact counts, regression test reduction metrics, and the Benchmark vs. Live comparison panel.
   - **Tab 2: Core Differentiators:** Inspect the Graph vs. Semantic contrast, the Decoy Rejection Inspector, and Uncertainty Surfacing.
   - **Tab 3: Multi-Layer Graph:** Interactive graph visualization of structural nodes, semantically recovered nodes, and test links.
   - **Tab 4: Semantic Candidate Gate:** Table of all candidate artifacts evaluated by the Context Filter with rejection reasons.
   - **Tab 5: Safety Gate Invariant:** Safety invariant status ($T_{safe} \subseteq T_{selected}$) and interactive **Simulate Safety Exclusion Attack** demo.
   - **Tab 6: Auditable Evidence:** Full latency breakdown and JSON evidence trail export.

---

## 5. How to Execute the Primary Demonstrations

### Demo A: Hidden Semantic Dependency (Graph Blindness)
1. Select **Scenario 2** in the sidebar.
2. Observe in Tab 2:
   - **Graph Traversal:** 0 impacts found (broken/missing explicit `.arxml` link).
   - **Contextual Semantic:** Candidate `SWC_AEB_FusedTargetHandler` recovered.
   - **Context Gate:** Evaluated as `ACCEPTED` (ADAS == ADAS, ECU_ADAS_Front == ECU_ADAS_Front).
   - **Safety Test:** `TC_AEB_002` (ASIL-D) automatically selected.

### Demo B: Semantic Decoy Rejection
1. Select **Scenario 3** in the sidebar.
2. In Tab 2 ("Semantic Decoy Rejection Inspector"):
   - Observe `SWC_BodyLightController` (Body Electronics) has high raw textual similarity (0.782).
   - The Context Gate rejects it: `"Subsystem mismatch: Candidate belongs to 'Body_Electronics', expected 'ADAS'"`.
   - Result: False positive prevented!

### Demo C: Regression Test Suite Reduction
1. Select **Scenario 6** in the sidebar.
2. View Tab 1 ("Executive Summary"):
   - Total test suite: 100 tests.
   - Selected tests: 4 tests.
   - Tests avoided: 96 tests (**96.0% reduction**).
   - Safety tests retained: 100% of mandatory ASIL-D tests.

### Demo D: Safety Gate Invariant Enforcement
1. Navigate to Tab 5 ("Safety Gate Invariant").
2. Check the safety panel: $T_{safe} \subseteq T_{selected}$ is `PASS (100% Retained)`.
3. Click the interactive button: **"Simulate Safety Exclusion Attack"**.
4. The system simulates an optimizer trying to deselect ASIL-D tests, and the Safety Gate immediately triggers: **`SAFETY GATE INTERVENTION: BLOCKED & REPAIRED`**, restoring mandatory tests.

---

## 6. How to Run Automated Validation

Execute the 12-scenario validation script:
```bash
python scripts/run_round2_validation.py
```

Generated outputs:
- `validation/round2/validation_summary.json`: Detailed pass/fail record of all 12 scenarios.
- `validation/round2/performance.csv`: Precise latency breakdown per pipeline stage.
- `validation/round2/failures/adversarial_failures.csv`: Logged adversarial failure cases.

---

## 7. How to Reproduce Benchmark Comparisons

To view or verify the frozen research benchmark evidence:
- Inspect canonical results summary: `reports/final/METRIC_INTEGRITY_AUDIT.md`.
- Inspect final evidence document: `reports/final/FINAL_RELEASE_EVIDENCE_INTEGRITY.md`.
- The dashboard automatically displays the authoritative benchmark comparison in Tab 1 without mixing live demonstration outputs with research metrics.

---

## 8. How to Inspect Evidence & Audit Trails

1. **In the Web UI:** Go to Tab 6 ("Auditable Evidence") and click `"Download Audit Report (JSON)"`.
2. **Via CLI:** Run any change analysis script (e.g. `python scripts/run_round2_validation.py`) and inspect the generated JSON files in `validation/round2/`.

---

## 9. How to Run Automated Unit & Integration Tests

Run the full test suite:
```bash
python -m pytest tests/ -q
```
Expected output:
```
........................................................................ [ 28%]
........................................................................ [ 57%]
........................................................................ [ 85%]
....................................                                     [100%]
252 passed in 7.12s
```

Run only Round 2 demonstrator tests:
```bash
python -m pytest tests/round2/test_round2_demonstrator.py -v
```
Expected: 32 passed.
