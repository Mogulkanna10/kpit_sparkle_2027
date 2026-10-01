# AURA-Impact v6: Out-of-Distribution (OOD) Generator B Integrity Audit

- **In-Distribution HSR (Generator A):** $40.67\%$
- **Out-of-Distribution HSR (Generator B):** $20.00\%$ (Graph-Only: $0.00\%$)
- **Absolute Degradation:** $-20.67$ percentage points.
- **Relative Degradation:** $-50.8\%$.
- **Scientific Characterization:**
  - This result is characterized as **moderate vocabulary shift degradation**, NOT "strong generalization".
  - It demonstrates that while the model retains positive recovery capability on completely novel sentence structures ($20.00\%$ vs $0.00\%$ for graph), subword hashing without domain fine-tuning experiences expected transfer loss.
