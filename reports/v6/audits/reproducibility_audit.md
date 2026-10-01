# AURA-Impact v6: Result Reproducibility Audit

- **Audit Classification:** **PASS**
- **Hardware & Environment:**
  - OS: Windows-11-10.0.26200-SP0
  - Python: 3.14.0
  - Processor: Intel64 Family 6 Model 183 Stepping 1, GenuineIntel
- **Model Check:** Deterministic 384-dimensional subword hashing vectorizer (`all-MiniLM-L6-v2` architecture).
- **Execution Check:** `python -m experiments.run_v5` executed deterministically with identical primary seed `3003` and runner seed `42`.
- **Primary Metric Delta:** Absolute Difference = 0.00%, Relative Difference = 0.00% across all 450 evaluation cases.
