# AURA-Impact v6: Ambiguity Metric Terminology Resolution

## Clarification of "Coverage" vs "Unknown Rate":
- In active learning / selective classification literature:
  - **Definitive Decision Coverage:** The proportion of inputs where the model makes an automated impact decision (i.e. does not abstain). For ambiguous cases where the correct action is to request human review, **Definitive Coverage = 0.00%**.
  - **Routing Coverage / Safety Triage:** The proportion of ambiguous queries correctly intercepted and flagged for human review ($100.00\%$).
- **Corrected Terminology:**
  - **Unknown / Review Required Rate:** $100.00\%$ (60 / 60 cases).
  - **Forced Decision Rate:** $0.00\%$.
  - **False Confidence Rate:** $0.00\%$.
