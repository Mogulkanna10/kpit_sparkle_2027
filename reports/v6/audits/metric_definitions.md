# AURA-Impact v6: Mathematical Metric Definitions

1. **Hidden Semantic Recall (HSR):**
   $$\text{HSR} = \frac{|T_{pred} \cap T_{true}^*|}{|T_{true}^*|}$$
   - **Level:** Macro-averaged across all $N=150$ HIDDEN_SEMANTIC cases.
2. **Artifact Precision:**
   $$\text{Precision} = \frac{|T_{pred} \cap T_{true}^*|}{|T_{pred}|} \quad (\text{defined as } 1.0 \text{ if } |T_{pred}| = |T_{true}^*| = 0)$$
3. **Artifact F1-Score:**
   $$\text{F1} = \frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} \quad (\text{defined as } 1.0 \text{ if } |T_{pred}| = |T_{true}^*| = 0)$$
4. **Semantic Decoy False Positive Rate (SFPR):**
   $$\text{SFPR} = \frac{\text{Number of cases with } |T_{pred}| > 0 \text{ or decoy retrieved}}{\text{Total Decoy Cases}}$$
5. **Decoy Specificity:**
   $$\text{Specificity} = 1 - \text{SFPR} = \frac{\text{Number of cases with } |T_{pred}| = 0}{\text{Total Decoy Cases}}$$
6. **Hidden Impacted Test Recall (HTR):**
   $$\text{HTR} = \frac{|T_{selected} \cap T_{test}^*|}{|T_{test}^*|}$$
7. **Regression Test Suite Reduction:**
   $$\text{Reduction} = 1 - \frac{|T_{selected}|}{|T_{total}|}$$
8. **Safety-Critical Test Invariant:**
   $$\forall m, \quad T_{safe}^* \subseteq T_{selected} \iff \text{Safety Recall} = 100.00\%$$
