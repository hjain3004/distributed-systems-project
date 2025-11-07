"""
Validate distribution implementations

This script tests that our service time distributions generate samples
with the correct statistical properties (mean, variance, CV²).

Run this to verify distributions are working correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from src.core.distributions import ExponentialService, ParetoService


def test_exponential_distribution():
    """Test ExponentialService generates correct statistics"""
    print("=" * 70)
    print("Testing Exponential Distribution")
    print("=" * 70)

    service_rate = 12.0  # μ = 12 msg/sec/thread
    expected_mean = 1.0 / service_rate
    expected_variance = expected_mean ** 2
    expected_cv2 = 1.0  # CV² = 1 for exponential

    print(f"\nExpected: μ = {service_rate}, E[S] = {expected_mean:.6f}, CV² = {expected_cv2:.2f}")

    # Generate samples
    dist = ExponentialService(service_rate)
    samples = [dist.sample() for _ in range(100000)]

    # Calculate statistics
    sample_mean = np.mean(samples)
    sample_variance = np.var(samples, ddof=1)
    sample_cv2 = sample_variance / (sample_mean ** 2)

    print(f"Sampled:  E[S] = {sample_mean:.6f}, Var[S] = {sample_variance:.6f}, CV² = {sample_cv2:.2f}")

    # Check errors
    mean_error = abs(sample_mean - expected_mean) / expected_mean * 100
    cv2_error = abs(sample_cv2 - expected_cv2) / expected_cv2 * 100

    print(f"Errors:   Mean: {mean_error:.2f}%, CV²: {cv2_error:.2f}%")

    if mean_error < 1.0 and cv2_error < 5.0:
        print("✓ PASS: Exponential distribution is correct")
        return True
    else:
        print("✗ FAIL: Exponential distribution has errors")
        return False


def test_pareto_distribution():
    """Test ParetoService generates correct statistics"""
    print("\n" + "=" * 70)
    print("Testing Pareto Distribution")
    print("=" * 70)

    # Test multiple alpha values
    test_cases = [
        {"alpha": 2.1, "name": "Heavy-tail (α=2.1)"},
        {"alpha": 2.5, "name": "Moderate-tail (α=2.5)"},
        {"alpha": 3.0, "name": "Light-tail (α=3.0, should match exponential)"},
    ]

    all_passed = True

    for test_case in test_cases:
        alpha = test_case["alpha"]
        name = test_case["name"]

        print(f"\n--- {name} ---")

        # Target mean service time: 1/12 sec (same as exponential)
        service_rate = 12.0
        target_mean = 1.0 / service_rate

        # Calculate scale parameter: E[S] = α·k/(α-1) → k = E[S]·(α-1)/α
        scale = target_mean * (alpha - 1) / alpha

        # Expected statistics (using CORRECTED formulas)
        expected_mean = alpha * scale / (alpha - 1)
        expected_variance = (alpha * scale**2) / ((alpha - 1)**2 * (alpha - 2)) if alpha > 2 else float('inf')
        expected_cv2 = 1.0 / (alpha * (alpha - 2)) if alpha > 2 else float('inf')

        print(f"Parameters: α = {alpha}, k = {scale:.6f}")
        print(f"Expected: E[S] = {expected_mean:.6f}, CV² = {expected_cv2:.2f}")

        # Generate samples
        dist = ParetoService(alpha=alpha, scale=scale)
        samples = [dist.sample() for _ in range(100000)]

        # Calculate statistics
        sample_mean = np.mean(samples)
        sample_variance = np.var(samples, ddof=1)
        sample_cv2 = sample_variance / (sample_mean ** 2)

        print(f"Sampled:  E[S] = {sample_mean:.6f}, Var[S] = {sample_variance:.6f}, CV² = {sample_cv2:.2f}")

        # Check errors
        mean_error = abs(sample_mean - expected_mean) / expected_mean * 100
        cv2_error = abs(sample_cv2 - expected_cv2) / expected_cv2 * 100 if expected_cv2 != float('inf') else 0

        print(f"Errors:   Mean: {mean_error:.2f}%, CV²: {cv2_error:.2f}%")

        # Tolerance: mean within 2%, CV² within 10%
        if mean_error < 2.0 and cv2_error < 10.0:
            print(f"✓ PASS: Pareto α={alpha} is correct")
        else:
            print(f"✗ FAIL: Pareto α={alpha} has significant errors")
            all_passed = False

    return all_passed


def main():
    """Run all distribution validation tests"""
    print("\n" + "=" * 70)
    print(" DISTRIBUTION VALIDATION TESTS")
    print("=" * 70)

    exp_pass = test_exponential_distribution()
    pareto_pass = test_pareto_distribution()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Exponential: {'✓ PASS' if exp_pass else '✗ FAIL'}")
    print(f"Pareto:      {'✓ PASS' if pareto_pass else '✗ FAIL'}")

    if exp_pass and pareto_pass:
        print("\n✓ ALL TESTS PASSED")
    else:
        print("\n✗ SOME TESTS FAILED - DISTRIBUTIONS NEED FIXING")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
