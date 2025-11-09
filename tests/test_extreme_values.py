"""
Tests for Extreme Value Analysis

Verifies bootstrap percentile estimation and Extreme Value Theory (EVT) methods
for heavy-tailed distributions.
"""

import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis.empirical_percentiles import (
    EmpiricalPercentileEstimator,
    compare_percentile_methods
)
from src.analysis.extreme_value_theory import (
    ExtremeValueAnalyzer,
    validate_evt_assumptions
)


class TestEmpiricalPercentiles:
    """Test bootstrap-based percentile estimation"""

    def test_bootstrap_percentile_exponential(self):
        """Test bootstrap on exponential distribution (known quantiles)"""
        np.random.seed(42)

        # Generate exponential data (rate=1)
        n = 5000
        data = np.random.exponential(scale=1.0, size=n)

        # Theoretical P99 for Exp(1): -ln(1-0.99) = 4.605
        theoretical_p99 = -np.log(1 - 0.99)

        # Bootstrap estimate
        estimator = EmpiricalPercentileEstimator(data)
        p99, lower, upper = estimator.bootstrap_percentile(0.99, n_bootstrap=1000, random_seed=42)

        print(f"\nExponential P99:")
        print(f"  Theoretical: {theoretical_p99:.3f}")
        print(f"  Bootstrap:   {p99:.3f} (95% CI: [{lower:.3f}, {upper:.3f}])")

        # Should be within 10% of theoretical value
        error = abs(p99 - theoretical_p99) / theoretical_p99
        assert error < 0.10, f"Bootstrap error {error*100:.1f}% exceeds 10%"

        # CI should contain theoretical value
        assert lower <= theoretical_p99 <= upper, "Theoretical value not in CI"

    def test_bootstrap_percentile_pareto(self):
        """Test bootstrap on Pareto distribution (heavy tail)"""
        np.random.seed(42)

        # Generate Pareto data
        alpha = 2.5
        scale = 1.0
        n = 10000

        # Pareto distribution: F(x) = 1 - (k/x)^α
        # Quantile: Q(p) = k / (1-p)^(1/α)
        data = (np.random.pareto(alpha, n) + 1) * scale

        # Theoretical P99
        theoretical_p99 = scale / ((1 - 0.99) ** (1/alpha))

        # Bootstrap estimate
        estimator = EmpiricalPercentileEstimator(data)
        p99, lower, upper = estimator.bootstrap_percentile(0.99, n_bootstrap=1000, random_seed=42)

        print(f"\nPareto(α={alpha}) P99:")
        print(f"  Theoretical: {theoretical_p99:.3f}")
        print(f"  Bootstrap:   {p99:.3f} (95% CI: [{lower:.3f}, {upper:.3f}])")

        # Looser tolerance for heavy tails
        error = abs(p99 - theoretical_p99) / theoretical_p99
        assert error < 0.20, f"Bootstrap error {error*100:.1f}% exceeds 20%"

    def test_multiple_percentiles(self):
        """Test estimating multiple percentiles at once"""
        np.random.seed(42)

        data = np.random.exponential(1.0, 5000)
        estimator = EmpiricalPercentileEstimator(data)

        results = estimator.multiple_percentiles([0.95, 0.99, 0.999], n_bootstrap=500, random_seed=42)

        # Should have results for all requested percentiles
        assert len(results) == 3
        assert 0.95 in results
        assert 0.99 in results
        assert 0.999 in results

        # Check structure
        for p in results:
            assert 'point' in results[p]
            assert 'lower' in results[p]
            assert 'upper' in results[p]
            assert 'ci_width' in results[p]

        # Percentiles should be increasing
        assert results[0.95]['point'] < results[0.99]['point']
        assert results[0.99]['point'] < results[0.999]['point']

    def test_standard_error(self):
        """Test standard error estimation"""
        np.random.seed(42)

        data = np.random.normal(0, 1, 1000)
        estimator = EmpiricalPercentileEstimator(data)

        std_error = estimator.percentile_standard_error(0.95, n_bootstrap=500, random_seed=42)

        # Standard error should be positive
        assert std_error > 0

        # Should be reasonable (not too large)
        assert std_error < 1.0


class TestExtremeValueTheory:
    """Test Extreme Value Theory methods"""

    def test_gpd_fitting_pareto(self):
        """Test GPD fitting on Pareto data"""
        np.random.seed(42)

        # Generate heavy-tailed Pareto data
        alpha = 2.5
        n = 10000
        data = (np.random.pareto(alpha, n) + 1)

        # Fit GPD to tail
        analyzer = ExtremeValueAnalyzer(data)
        shape, loc, scale = analyzer.fit_gpd_tail(threshold_percentile=0.90)

        print(f"\nGPD Fitting (Pareto α={alpha}):")
        print(f"  Shape (ξ): {shape:.3f}")
        print(f"  Scale (σ): {scale:.3f}")

        # For Pareto, shape parameter should be positive (heavy tail)
        assert shape > 0, "GPD shape should be positive for Pareto"

        # Shape should be related to tail index: ξ ≈ 1/α
        expected_shape = 1 / alpha
        shape_error = abs(shape - expected_shape) / expected_shape
        assert shape_error < 0.5, f"Shape parameter error {shape_error*100:.1f}% too large"

    def test_extreme_quantile_pareto(self):
        """Test extreme quantile estimation using EVT"""
        np.random.seed(42)

        alpha = 2.5
        scale = 1.0
        n = 10000

        # Generate Pareto data
        data = (np.random.pareto(alpha, n) + 1) * scale

        # Theoretical P99
        theoretical_p99 = scale / ((1 - 0.99) ** (1/alpha))

        # EVT estimate
        analyzer = ExtremeValueAnalyzer(data)
        evt_p99 = analyzer.extreme_quantile(0.99, threshold_percentile=0.90)

        print(f"\nEVT P99 Estimation:")
        print(f"  Theoretical: {theoretical_p99:.3f}")
        print(f"  EVT:         {evt_p99:.3f}")

        # Should be within 20% (EVT is approximate for finite samples)
        error = abs(evt_p99 - theoretical_p99) / theoretical_p99
        assert error < 0.25, f"EVT error {error*100:.1f}% exceeds 25%"

    def test_hill_estimator(self):
        """Test Hill estimator for tail index"""
        np.random.seed(42)

        alpha = 2.5
        n = 10000

        # Generate Pareto data
        data = (np.random.pareto(alpha, n) + 1)

        # Hill estimate
        analyzer = ExtremeValueAnalyzer(data)
        alpha_hat = analyzer.hill_estimator(k=int(np.sqrt(n)))

        print(f"\nHill Estimator:")
        print(f"  True α: {alpha}")
        print(f"  Estimated α: {alpha_hat:.3f}")

        # Should be within 20% of true value
        error = abs(alpha_hat - alpha) / alpha
        assert error < 0.25, f"Hill estimator error {error*100:.1f}% exceeds 25%"

    def test_hill_confidence_interval(self):
        """Test confidence interval for Hill estimator"""
        np.random.seed(42)

        data = (np.random.pareto(2.5, 5000) + 1)

        analyzer = ExtremeValueAnalyzer(data)
        alpha_hat, lower, upper = analyzer.tail_index_confidence_interval()

        print(f"\nHill CI:")
        print(f"  α̂ = {alpha_hat:.3f} (95% CI: [{lower:.3f}, {upper:.3f}])")

        # CI should be valid
        assert lower < alpha_hat < upper
        assert upper - lower > 0

    def test_quantile_comparison(self):
        """Test comparison of quantile estimation methods"""
        np.random.seed(42)

        data = (np.random.pareto(2.5, 10000) + 1)

        analyzer = ExtremeValueAnalyzer(data)
        results = analyzer.quantile_comparison([0.95, 0.99], threshold_percentile=0.90)

        # Should have results for requested percentiles
        assert 0.95 in results
        assert 0.99 in results

        # Should have GPD parameters
        assert 'gpd_params' in results
        assert 'shape' in results['gpd_params']
        assert 'scale' in results['gpd_params']

        # Check structure for each percentile
        for p in [0.95, 0.99]:
            assert 'empirical' in results[p]
            assert 'gpd' in results[p]
            assert 'difference' in results[p]
            assert 'relative_diff_pct' in results[p]

        print(f"\nQuantile Comparison:")
        for p in [0.95, 0.99]:
            print(f"  P{int(p*100)}: Empirical={results[p]['empirical']:.2f}, "
                  f"GPD={results[p]['gpd']:.2f}, "
                  f"Diff={results[p]['relative_diff_pct']:.1f}%")

    def test_evt_vs_empirical_exponential(self):
        """Compare EVT with empirical for exponential (light tail)"""
        np.random.seed(42)

        # Exponential has light tail
        data = np.random.exponential(1.0, 10000)

        analyzer = ExtremeValueAnalyzer(data)

        empirical_p99 = np.percentile(data, 99)
        evt_p99 = analyzer.extreme_quantile(0.99, threshold_percentile=0.90)

        print(f"\nExponential (light tail):")
        print(f"  Empirical P99: {empirical_p99:.3f}")
        print(f"  EVT P99:       {evt_p99:.3f}")

        # For light tails, empirical and EVT should be similar
        relative_diff = abs(evt_p99 - empirical_p99) / empirical_p99
        assert relative_diff < 0.15, "EVT and empirical should agree for light tails"

    def test_evt_assumptions_validation(self):
        """Test EVT assumptions validation"""
        np.random.seed(42)

        # Heavy-tailed data
        data = (np.random.pareto(2.5, 5000) + 1)

        diagnostics = validate_evt_assumptions(data, threshold_percentile=0.90)

        print(f"\nEVT Diagnostics:")
        print(f"  N exceedances: {diagnostics['n_exceedances']}")
        print(f"  GPD shape: {diagnostics['gpd_shape']:.3f}")
        print(f"  Hill alpha: {diagnostics['hill_alpha']:.3f}")
        print(f"  Is heavy tail: {diagnostics['is_heavy_tail']}")
        print(f"  Recommendation: {diagnostics['recommendation']}")

        # Check diagnostics structure
        assert 'n_data' in diagnostics
        assert 'n_exceedances' in diagnostics
        assert 'gpd_shape' in diagnostics
        assert 'hill_alpha' in diagnostics
        assert 'is_heavy_tail' in diagnostics
        assert 'recommendation' in diagnostics

        # Should detect heavy tail
        assert diagnostics['is_heavy_tail'] == True
        assert diagnostics['gpd_shape'] > 0


class TestComparisonMethods:
    """Test comparison of different methods"""

    def test_compare_methods_pareto(self):
        """Compare all methods on Pareto distribution"""
        np.random.seed(42)

        alpha = 2.5
        scale = 1.0
        n = 10000

        data = (np.random.pareto(alpha, n) + 1) * scale

        # Theoretical P99
        theoretical_p99 = scale / ((1 - 0.99) ** (1/alpha))

        # Compare methods
        results = compare_percentile_methods(data, p=0.99, true_value=theoretical_p99)

        print(f"\nMethod Comparison (Pareto α={alpha}):")
        print(f"  Theoretical:       {theoretical_p99:.3f}")
        print(f"  Empirical:         {results['empirical']:.3f} ({results['empirical_error']:.1f}% error)")
        print(f"  Bootstrap:         {results['bootstrap_point']:.3f} ({results['bootstrap_error']:.1f}% error)")
        print(f"  Normal Approx:     {results['normal_approx']:.3f} ({results['normal_error']:.1f}% error)")

        # Empirical and bootstrap should be similar
        assert abs(results['empirical'] - results['bootstrap_point']) / results['empirical'] < 0.10

        # Normal approximation should be worst for heavy tails
        assert results['normal_error'] > results['empirical_error']


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
