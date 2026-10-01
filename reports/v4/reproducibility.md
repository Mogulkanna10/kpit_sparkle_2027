# AURA-Impact v4: Reproducibility & Environment Specification

- **Python Version:** 3.14.0 (Windows x86_64)
- **Random Seeds:** Primary Benchmark: `3003`, Held-Out Generator: `9999`, Pytest / Runner: `42`
- **Embedding Model:** `all-MiniLM-L6-v2` / Deterministic Subword Vectorizer (384 dimensions)
- **Calibrated Parameters:**
  - Semantic Cosine Threshold: `0.30`
  - Top-K Candidate Limit: `10`
  - Context Weights: $\alpha=0.20, \beta=0.15, \gamma=0.10, \delta=0.05$
- **Total Primary Cases:** 450 (120 Structural, 150 Hidden Semantic, 120 Decoy, 60 Ambiguous)
- **Decoy Stress Cases:** 200 (10 Decoy Sub-Types D1 to D10)
- **Held-Out Generator Cases:** 60 (Generator B)
- **Execution Script:** `python experiments/run_v4_final_validation.py`
- **Automated Verification:** `python -m pytest tests/`
