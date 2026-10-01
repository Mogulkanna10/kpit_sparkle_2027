# DEMONSTRATION DATASET (SYNTHETIC)
## KPIT Sparkle 2027 Round 2 — AURA-Impact Engineering Demonstrator

> **DISCLAIMER:** This dataset is a **synthetic engineering demonstration project** created strictly for evaluating and demonstrating the AURA-Impact change-impact analysis engine. It does **NOT** contain proprietary OEM or Tier-1 software.

### Subsystem Topology
- **ADAS Subsystem (ECU_1, ASIL-D):** Autonomous Emergency Braking (AEB), Radar processing, Time-to-Collision (TTC) calculation, emergency hydraulic deceleration clamping.
- **Body Electronics (ECU_Body, QM):** Cabin climate defroster, blower power level, interior comfort (includes semantic decoy with overlapping terminology).
- **Powertrain (ECU_Engine, ASIL-B/C):** Adaptive Cruise Control (ACC) target velocity modulation.
- **Regression Suite:** 100 structured test cases across ASIL-D, ASIL-B, and QM safety classes.
