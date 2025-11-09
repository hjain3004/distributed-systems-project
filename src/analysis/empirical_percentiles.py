"""
Empirical Percentile Estimation for Heavy-Tailed Distributions

Bootstrap-based percentile estimation with confidence intervals.
Particularly useful for heavy-tailed distributions where analytical
methods may be unreliable.
"""

import numpy as np
from typing import Tuple, Optional


class EmpiricalPercentileEstimator:
    """
    Bootstrap-based percentile estimation for heavy-tailed distributions

    This method makes no distributional assumptions and works well even
    when the distribution has heavy tails or infinite variance.

    Reference:
    Efron, B., & Tibshirani, R. J. (1994). An introduction to the bootstrap.
    CRC press.
    """

    def __init__(self, data: np.ndarray, confidence_level: float = 0.95):
        """
        Args:
            data: Empirical data samples
            confidence_level: Confidence level for intervals (default 0.95)
        """
        self.data = np.asarray(data)
        self.confidence_level = confidence_level

        if len(self.data) == 0:
            raise ValueError("Data array cannot be empty")

    def bootstrap_percentile(self,
                            p: float,
                            n_bootstrap: int = 10000,
                            random_seed: Optional[int] = None) -> Tuple[float, float, float]:
        """
        Bootstrap confidence interval for pth percentile

        Args:
            p: Percentile (e.g., 0.99 for P99)
            n_bootstrap: Number of bootstrap samples (default 10000)
            random_seed: Random seed for reproducibility

        Returns:
            (point_estimate, lower_bound, upper_bound)

        Example:
            >>> data = np.random.pareto(2.5, 10000)
            >>> estimator = EmpiricalPercentileEstimator(data)
            >>> p99, lower, upper = estimator.bootstrap_percentile(0.99)
            >>> print(f"P99 = {p99:.3f} (95% CI: [{lower:.3f}, {upper:.3f}])")
        """
        if not 0 <= p <= 1:
            raise ValueError("Percentile p must be in [0, 1]")

        if random_seed is not None:
            np.random.seed(random_seed)

        n = len(self.data)
        percentiles = np.zeros(n_bootstrap)

        # Generate bootstrap samples
        for i in range(n_bootstrap):
            # Resample with replacement
            bootstrap_sample = np.random.choice(self.data, size=n, replace=True)
            percentiles[i] = np.percentile(bootstrap_sample, p * 100)

        # Calculate confidence interval
        alpha = 1 - self.confidence_level
        lower = np.percentile(percentiles, alpha/2 * 100)
        upper = np.percentile(percentiles, (1 - alpha/2) * 100)

        # Point estimate from original data
        point = np.percentile(self.data, p * 100)

        return point, lower, upper

    def multiple_percentiles(self,
                            percentiles: list,
                            n_bootstrap: int = 10000,
                            random_seed: Optional[int] = None) -> dict:
        """
        Estimate multiple percentiles with confidence intervals

        Args:
            percentiles: List of percentiles to estimate (e.g., [0.95, 0.99, 0.999])
            n_bootstrap: Number of bootstrap samples
            random_seed: Random seed for reproducibility

        Returns:
            Dictionary mapping percentile to (point, lower, upper)
        """
        results = {}

        for p in percentiles:
            point, lower, upper = self.bootstrap_percentile(
                p, n_bootstrap, random_seed
            )
            results[p] = {
                'point': point,
                'lower': lower,
                'upper': upper,
                'ci_width': upper - lower
            }

        return results

    def percentile_standard_error(self,
                                  p: float,
                                  n_bootstrap: int = 10000,
                                  random_seed: Optional[int] = None) -> float:
        """
        Estimate standard error of percentile using bootstrap

        Args:
            p: Percentile to estimate
            n_bootstrap: Number of bootstrap samples
            random_seed: Random seed

        Returns:
            Standard error estimate
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        n = len(self.data)
        percentiles = np.zeros(n_bootstrap)

        for i in range(n_bootstrap):
            bootstrap_sample = np.random.choice(self.data, size=n, replace=True)
            percentiles[i] = np.percentile(bootstrap_sample, p * 100)

        return np.std(percentiles, ddof=1)

    def percentile_bias(self,
                       p: float,
                       n_bootstrap: int = 10000,
                       random_seed: Optional[int] = None) -> float:
        """
        Estimate bias in percentile estimate using bootstrap

        Args:
            p: Percentile to estimate
            n_bootstrap: Number of bootstrap samples
            random_seed: Random seed

        Returns:
            Estimated bias
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        n = len(self.data)
        percentiles = np.zeros(n_bootstrap)

        for i in range(n_bootstrap):
            bootstrap_sample = np.random.choice(self.data, size=n, replace=True)
            percentiles[i] = np.percentile(bootstrap_sample, p * 100)

        # Bias = E[θ̂] - θ
        original_percentile = np.percentile(self.data, p * 100)
        bootstrap_mean = np.mean(percentiles)

        return bootstrap_mean - original_percentile


def compare_percentile_methods(data: np.ndarray,
                               p: float = 0.99,
                               true_value: Optional[float] = None) -> dict:
    """
    Compare different percentile estimation methods

    Args:
        data: Empirical data
        p: Percentile to estimate
        true_value: True theoretical value (if known)

    Returns:
        Dictionary with comparison results
    """
    estimator = EmpiricalPercentileEstimator(data)

    # Empirical percentile (no bootstrap)
    empirical = np.percentile(data, p * 100)

    # Bootstrap estimate with CI
    bootstrap_point, bootstrap_lower, bootstrap_upper = estimator.bootstrap_percentile(p)

    # Standard error
    std_error = estimator.percentile_standard_error(p)

    # Normal approximation (for comparison)
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    z_score = {0.95: 1.645, 0.99: 2.326, 0.999: 3.090}.get(p, 2.326)
    normal_approx = mean + z_score * std

    results = {
        'empirical': empirical,
        'bootstrap_point': bootstrap_point,
        'bootstrap_ci': (bootstrap_lower, bootstrap_upper),
        'bootstrap_std_error': std_error,
        'normal_approx': normal_approx,
    }

    if true_value is not None:
        results['empirical_error'] = abs(empirical - true_value) / true_value * 100
        results['bootstrap_error'] = abs(bootstrap_point - true_value) / true_value * 100
        results['normal_error'] = abs(normal_approx - true_value) / true_value * 100

    return results
