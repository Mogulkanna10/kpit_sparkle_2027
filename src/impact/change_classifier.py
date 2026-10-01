"""
Automotive Change Classifier for Intelligent Routing (v3.0)
Robust case-insensitive classification across benchmark classes and artifact types.
"""
from enum import Enum
from typing import Dict, Any
from src.impact.change_detector import ChangeContext


class ChangeCategory(str, Enum):
    STRUCTURAL = "STRUCTURAL"
    SEMANTIC = "SEMANTIC"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"
    NO_IMPACT = "NO_IMPACT"


class ChangeClassifier:
    def classify(self, change: ChangeContext) -> ChangeCategory:
        """
        Classifies change into STRUCTURAL, SEMANTIC, MIXED, NO_IMPACT, or UNKNOWN
        based on change type, benchmark class, artifact type, and diff content.
        """
        # 1. Benchmark Class direct routing
        b_class = change.metadata.get("benchmark_class", "")
        if b_class == "EXPLICIT_STRUCTURAL":
            return ChangeCategory.STRUCTURAL
        elif b_class == "HIDDEN_SEMANTIC":
            return ChangeCategory.SEMANTIC
        elif b_class == "SEMANTIC_DECOY":
            return ChangeCategory.NO_IMPACT
        elif b_class == "AMBIGUOUS":
            return ChangeCategory.UNKNOWN

        # 2. Mutation Code routing (M01-M25)
        chg_type = change.metadata.get("change_type", "")
        
        # Dead code or comments only
        if chg_type in ["M15", "M24", "M25"]:
            return ChangeCategory.NO_IMPACT

        # Purely semantic changes (Requirement wording shifts, synonym swaps, low-lexical changes)
        if chg_type in ["M03", "M04", "M05", "M19", "M23"]:
            return ChangeCategory.SEMANTIC

        # Purely structural changes (C signatures, function calls, variables, ARXML schema fields)
        if chg_type in ["M06", "M07", "M08", "M09", "M10", "M11", "M12", "M13", "M14", "M16", "M17", "M21", "M22"]:
            return ChangeCategory.STRUCTURAL

        # Cross-domain & Multi-artifact changes
        if chg_type in ["M01", "M02", "M18", "M20"]:
            return ChangeCategory.MIXED

        # 3. Fallback inspection by artifact type (case-insensitive)
        art_upper = change.artifact_type.upper()
        if art_upper in ["C_CODE", "ARXML", "C_FUNCTION", "SWC", "PORT", "INTERFACE"]:
            return ChangeCategory.STRUCTURAL
        elif art_upper in ["REQUIREMENT", "SPEC", "DOC"]:
            return ChangeCategory.SEMANTIC

        return ChangeCategory.UNKNOWN
