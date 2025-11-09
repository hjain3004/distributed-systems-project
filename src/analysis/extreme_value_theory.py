"""
Extreme Value Theory (EVT) for Tail Estimation

Uses Generalized Pareto Distribution (GPD) to model distribution tails
and estimate extreme quantiles (P99, P99.9, etc.).

Particularly useful for heavy-tailed distributions where normal approximations
fail catastrophically.

Reference:
McNeil, A. J., Frey, R., & Embrechts, P. (2015).
Quantitative risk management: concepts, techniques and tools.
Princeton University Press.
"""

import numpy as np
from scipy.stats import genpareto
from typing import Tuple, Optional
import warnings


class ExtremeValueAnalyzer:
    """
    Use Generalized Pareto Distribution (GPD) for tail modeling

    The GPD is the limiting distribution of exceedances over a high threshold.
    This is formalized by the Pickands-Balkema-de Haan theorem.

    GPD PDF: f(x) = (1/σ) * (1 + ξ(x-μ)/σ)^(-(1+1/ξ))

    where:
    - μ: location parameter (threshold)
    - σ: scale parameter
    - ξ: shape parameter (determines tail behavior)
      - ξ > 0: Heavy tail (Pareto-type)
      - ξ = 0: Exponential tail
      - ξ < 0: Short tail (bounded)
    """

    def __init__(self, data: np.ndarray):
        """
        Args:
            data: Empirical data samples (will be sorted internally)
        """
        self.data = np.sort(np.asarray(data))

        if len(self.data) == 0:
            raise ValueError("Data array cannot be empty")

    def fit_gpd_tail(self,
                     threshold_percentile: float = 0.90,
                     method: str = 'mle') -> Tuple[float, float, float]:
        """
        Fit GPD to exceedances over high threshold

        Args:
            threshold_percentile: Where to start tail modeling (default 90th percentile)
            method: Fitting method ('mle' for maximum likelihood)

        Returns:
            (shape, loc, scale) parameters of fitted GPD

        Note:
            The threshold choice is critical:
            - Too low: model bias (body affects tail estimate)
            - Too high: high variance (few exceedances)
            - Rule of thumb: use 90-95th percentile
        """
        if not 0.5 <= threshold_percentile < 1.0:
            raise ValueError("Threshold percentile should be in [0.5, 1.0)")

        # Calculate threshold
        threshold = np.percentile(self.data, threshold_percentile * 100)

        # Extract exceedances (values above threshold)
        exceedances = self.data[self.data > threshold] - threshold

        if len(exceedances) < 10:
            warnings.warn(
                f"Only {len(exceedances)} exceedances found. "
                "Consider lowering threshold_percentile for better estimates."
            )

        # Fit GPD using maximum likelihood
        # loc is fixed at 0 (we already subtracted threshold)
        shape, loc, scale = genpareto.fit(exceedances, floc=0)

        return shape, loc, scale

    def extreme_quantile(self,
                        p: float,
                        threshold_percentile: float = 0.90,
                        method: str = 'gpd') -> float:
        """
        Estimate extreme quantiles using fitted GPD

        Args:
            p: Desired quantile (e.g., 0.99 for P99)
            threshold_percentile: Threshold for tail fitting
            method: 'gpd' for Generalized Pareto, 'empirical' for direct

        Returns:
            Estimated quantile value

        Example:
            >>> data = np.random.pareto(2.5, 10000)
            >>> analyzer = ExtremeValueAnalyzer(data)
            >>> p99 = analyzer.extreme_quantile(0.99)
        """
        if not 0 <= p <= 1:
            raise ValueError("Quantile p must be in [0, 1]")

        if method == 'empirical':
            return np.percentile(self.data, p * 100)

        # Use empirical quantile below threshold
        if p <= threshold_percentile:
            return np.percentile(self.data, p * 100)

        # For extreme quantiles, use GPD
        threshold = np.percentile(self.data, threshold_percentile * 100)
        shape, loc, scale = self.fit_gpd_tail(threshold_percentile)

        # Number of exceedances
        n = len(self.data)
        n_exceed = np.sum(self.data > threshold)

        # Tail probability
        p_exceed = n_exceed / n

        # GPD quantile formula (Pickands-Balkema-de Haan theorem)
        if abs(shape) < 1e-10:
            # Exponential tail case (ξ ≈ 0)
            quantile = threshold + scale * np.log((1 - threshold_percentile) / (1 - p))
        else:
            # Pareto-type tail (ξ ≠ 0)
            # Q(p) = u + (σ/ξ) * [((1-u)/(1-p))^ξ - 1]
            # where u is the threshold percentile
            quantile = threshold + (scale / shape) * (
                ((1 - threshold_percentile) / (1 - p)) ** shape - 1
            )

        return quantile

    def hill_estimator(self, k: Optional[int] = None) -> float:
        """
        Hill estimator for tail index (α) of Pareto distribution

        For heavy-tailed distributions F(x) ~ x^(-α), the Hill estimator
        provides a simple estimate of α.

        Args:
            k: Number of order statistics to use (default: sqrt(n))

        Returns:
            Estimated tail index α

        Note:
            For Pareto distribution with shape parameter ξ: α = 1/ξ
            Larger α → lighter tail
            Smaller α → heavier tail

        Reference:
            Hill, B. M. (1975). A simple general approach to inference about
            the tail of a distribution. The Annals of Statistics, 3(5), 1163-1174.
        """
        n = len(self.data)

        if k is None:
            # Rule of thumb: k ≈ √n
            k = int(np.sqrt(n))

        if k >= n:
            raise ValueError(f"k ({k}) must be less than data size ({n})")

        if k < 2:
            raise ValueError("k must be at least 2")

        # Use k largest order statistics
        largest_k = self.data[-k:]
        threshold = self.data[-(k+1)]

        # Hill estimator: H_k = (1/k) * Σ log(X_i / X_(n-k))
        log_ratios = np.log(largest_k / threshold)
        alpha = k / np.sum(log_ratios)

        return alpha

    def mean_excess_plot_data(self, num_thresholds: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate data for mean excess plot (diagnostic tool)

        The mean excess plot helps choose appropriate threshold for GPD fitting.
        For GPD, mean excess should be approximately linear above threshold.

        Returns:
            (thresholds, mean_excesses) arrays for plotting

        Usage:
            >>> analyzer = ExtremeValueAnalyzer(data)
            >>> thresholds, excesses = analyzer.mean_excess_plot_data()
            >>> plt.plot(thresholds, excesses)
            >>> plt.xlabel('Threshold')
            >>> plt.ylabel('Mean Excess')
        """
        # Use quantiles as thresholds
        percentiles = np.linspace(50, 99, num_thresholds)
        thresholds = np.percentile(self.data, percentiles)

        mean_excesses = np.zeros(num_thresholds)

        for i, threshold in enumerate(thresholds):
            exceedances = self.data[self.data > threshold] - threshold
            if len(exceedances) > 0:
                mean_excesses[i] = np.mean(exceedances)
            else:
                mean_excesses[i] = np.nan

        return thresholds, mean_excesses

    def quantile_comparison(self,
                           percentiles: list = [0.95, 0.99, 0.999],
                           threshold_percentile: float = 0.90) -> dict:
        """
        Compare GPD-based quantiles with empirical quantiles

        Args:
            percentiles: List of percentiles to compare
            threshold_percentile: Threshold for GPD fitting

        Returns:
            Dictionary with comparison results
        """
        results = {}

        # Fit GPD once
        shape, loc, scale = self.fit_gpd_tail(threshold_percentile)

        for p in percentiles:
            empirical = np.percentile(self.data, p * 100)
            gpd_estimate = self.extreme_quantile(p, threshold_percentile, method='gpd')

            results[p] = {
                'empirical': empirical,
                'gpd': gpd_estimate,
                'difference': gpd_estimate - empirical,
                'relative_diff_pct': abs(gpd_estimate - empirical) / empirical * 100
            }

        # Add GPD parameters
        results['gpd_params'] = {
            'shape': shape,
            'scale': scale,
            'threshold': np.percentile(self.data, threshold_percentile * 100)
        }

        return results

    def tail_index_confidence_interval(self,
                                      k: Optional[int] = None,
                                      confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Confidence interval for Hill estimator of tail index

        Args:
            k: Number of order statistics
            confidence: Confidence level

        Returns:
            (alpha_hat, lower, upper)

        Note:
            Asymptotically, Hill estimator is normally distributed:
            √k (α̂ - α) ~ N(0, α²)
        """
        n = len(self.data)

        if k is None:
            k = int(np.sqrt(n))

        # Hill estimate
        alpha_hat = self.hill_estimator(k)

        # Asymptotic variance: Var(α̂) = α² / k
        std_error = alpha_hat / np.sqrt(k)

        # Confidence interval
        from scipy.stats import norm
        z = norm.ppf((1 + confidence) / 2)

        lower = alpha_hat - z * std_error
        upper = alpha_hat + z * std_error

        return alpha_hat, lower, upper


def validate_evt_assumptions(data: np.ndarray,
                             threshold_percentile: float = 0.90) -> dict:
    """
    Validate assumptions for EVT application

    Returns diagnostic information about data suitability for EVT

    Args:
        data: Empirical data
        threshold_percentile: Threshold for analysis

    Returns:
        Dictionary with diagnostic results
    """
    analyzer = ExtremeValueAnalyzer(data)

    # 1. Check for sufficient exceedances
    threshold = np.percentile(data, threshold_percentile * 100)
    n_exceedances = np.sum(data > threshold)
    exceedance_ratio = n_exceedances / len(data)

    # 2. Estimate tail index
    alpha_hat, alpha_lower, alpha_upper = analyzer.tail_index_confidence_interval()

    # 3. Fit GPD
    shape, loc, scale = analyzer.fit_gpd_tail(threshold_percentile)

    # 4. Check heavy-tail evidence
    is_heavy_tail = shape > 0.1  # ξ > 0 suggests heavy tail

    diagnostics = {
        'n_data': len(data),
        'n_exceedances': n_exceedances,
        'exceedance_ratio': exceedance_ratio,
        'threshold': threshold,
        'hill_alpha': alpha_hat,
        'hill_alpha_ci': (alpha_lower, alpha_upper),
        'gpd_shape': shape,
        'gpd_scale': scale,
        'is_heavy_tail': is_heavy_tail,
        'sufficient_exceedances': n_exceedances >= 10,
        'recommendation': 'GPD suitable' if n_exceedances >= 10 and is_heavy_tail else 'Use empirical percentiles'
    }

    return diagnostics
