"""
Statistical Rigor: Paired Tests, Bootstrap Confidence Intervals, and Significance
"""
from typing import List, Dict, Any, Tuple
import numpy as np
from scipy import stats


class BenchmarkStatistics:
    @staticmethod
    def bootstrap_ci(
        data: List[float],
        n_bootstraps: int = 1000,
        ci: float = 0.95,
        seed: int = 42
    ) -> Tuple[float, float, float, float]:
        """
        Returns (mean, median, ci_lower, ci_upper, std_dev)
        """
        arr = np.array(data)
        if len(arr) == 0:
            return 0.0, 0.0, 0.0, 0.0

        mean = float(np.mean(arr))
        median = float(np.median(arr))
        std = float(np.std(arr))

        if len(arr) == 1:
            return mean, median, mean, mean

        rng = np.random.default_rng(seed)
        boot_means = [np.mean(rng.choice(arr, size=len(arr), replace=True)) for _ in range(n_bootstraps)]
        
        alpha = (1.0 - ci) / 2.0
        ci_lower = float(np.percentile(boot_means, alpha * 100))
        ci_upper = float(np.percentile(boot_means, (1.0 - alpha) * 100))

        return mean, median, ci_lower, ci_upper

    @staticmethod
    def paired_wilcoxon_test(sample_a: List[float], sample_b: List[float]) -> Dict[str, Any]:
        """
        Wilcoxon signed-rank test for non-normal paired continuous differences.
        """
        diff = np.array(sample_a) - np.array(sample_b)
        # Filter zero differences
        nonzero_diff = diff[diff != 0]

        if len(nonzero_diff) < 5:
            return {
                "test": "Wilcoxon Signed-Rank Test",
                "statistic": 0.0,
                "p_value": 1.0,
                "is_significant": False,
                "note": "Insufficient non-zero paired differences (N < 5)"
            }

        try:
            stat, p_val = stats.wilcoxon(sample_a, sample_b)
            return {
                "test": "Wilcoxon Signed-Rank Test",
                "statistic": float(stat),
                "p_value": float(p_val),
                "is_significant": bool(p_val < 0.05),
                "mean_diff": float(np.mean(diff)),
                "median_diff": float(np.median(diff))
            }
        except Exception as e:
            return {
                "test": "Wilcoxon Signed-Rank Test",
                "statistic": 0.0,
                "p_value": 1.0,
                "is_significant": False,
                "error": str(e)
            }

    @staticmethod
    def mcnemar_test(binary_outcomes_a: List[bool], binary_outcomes_b: List[bool]) -> Dict[str, Any]:
        """
        McNemar test for paired 2x2 contingency table of binary detection outcomes.
        Table:
                Method B +   Method B -
        Method A +   n11          n10
        Method A -   n01          n00
        """
        n11 = n10 = n01 = n00 = 0
        for a, b in zip(binary_outcomes_a, binary_outcomes_b):
            if a and b:
                n11 += 1
            elif a and not b:
                n10 += 1
            elif not a and b:
                n01 += 1
            else:
                n00 += 1

        b_discordant = n10  # A won, B lost
        c_discordant = n01  # B won, A lost

        if (b_discordant + c_discordant) == 0:
            return {
                "test": "McNemar Test",
                "statistic": 0.0,
                "p_value": 1.0,
                "is_significant": False,
                "table": {"n11": n11, "n10": n10, "n01": n01, "n00": n00},
                "note": "Identical discordant counts (0 discordant pairs)"
            }

        # McNemar statistic with continuity correction: (|b - c| - 1)^2 / (b + c)
        chi2 = (abs(b_discordant - c_discordant) - 1) ** 2 / (b_discordant + c_discordant)
        p_val = stats.chi2.sf(chi2, df=1)

        return {
            "test": "McNemar Test",
            "statistic": float(chi2),
            "p_value": float(p_val),
            "is_significant": bool(p_val < 0.05),
            "table": {"n11": n11, "n10": n10, "n01": n01, "n00": n00},
            "discordant_a_only": n10,
            "discordant_b_only": n01
        }
