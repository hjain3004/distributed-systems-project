"""
Tests for Erlang Distribution and M/Ek/N Queue

Validates:
1. Erlang distribution properties
2. M/Ek/N queue implementation
3. Analytical formulas
4. Special cases (k=1, k→∞)
"""

import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.distributions import ErlangService
from src.models.mekn_queue import run_mekn_simulation, MEkNConfig
from src.analysis.analytical import MEkNAnalytical


class TestErlangDistribution:
    """Test Erlang distribution properties"""

    def test_erlang_mean(self):
        """Test E[S] = k/λ"""
        shape = 3
        rate = 12.0

        erlang = ErlangService(shape=shape, rate=rate)

        # Theoretical mean
        theoretical_mean = shape / rate

        # Empirical mean from samples
        samples = [erlang.sample() for _ in range(10000)]
        empirical_mean = np.mean(samples)

        print(f"\nErlang-{shape} Mean:")
        print(f"  Theoretical: {theoretical_mean:.4f}")
        print(f"  Empirical:   {empirical_mean:.4f}")

        # Should match within 5%
        error = abs(empirical_mean - theoretical_mean) / theoretical_mean
        assert error < 0.05, f"Mean error {error*100:.2f}% exceeds 5%"

    def test_erlang_variance(self):
        """Test Var[S] = k/λ²"""
        shape = 3
        rate = 12.0

        erlang = ErlangService(shape=shape, rate=rate)

        # Theoretical variance
        theoretical_var = shape / (rate ** 2)

        # Empirical variance from samples
        samples = [erlang.sample() for _ in range(10000)]
        empirical_var = np.var(samples, ddof=1)

        print(f"\nErlang-{shape} Variance:")
        print(f"  Theoretical: {theoretical_var:.6f}")
        print(f"  Empirical:   {empirical_var:.6f}")

        # Should match within 10%
        error = abs(empirical_var - theoretical_var) / theoretical_var
        assert error < 0.10, f"Variance error {error*100:.2f}% exceeds 10%"

    def test_erlang_cv_squared(self):
        """Test CV² = 1/k"""
        test_cases = [
            {'k': 1, 'expected_cv2': 1.0},     # Exponential
            {'k': 2, 'expected_cv2': 0.5},
            {'k': 4, 'expected_cv2': 0.25},
            {'k': 8, 'expected_cv2': 0.125},
        ]

        for case in test_cases:
            erlang = ErlangService(shape=case['k'], rate=10.0)

            # Theoretical CV²
            theoretical_cv2 = erlang.coefficient_of_variation()

            assert abs(theoretical_cv2 - case['expected_cv2']) < 1e-10, \
                f"CV² = 1/{case['k']} should equal {case['expected_cv2']}"

            # Empirical CV²
            samples = [erlang.sample() for _ in range(10000)]
            mean = np.mean(samples)
            var = np.var(samples, ddof=1)
            empirical_cv2 = var / (mean ** 2)

            print(f"\nErlang-{case['k']} CV²:")
            print(f"  Theoretical: {theoretical_cv2:.4f}")
            print(f"  Empirical:   {empirical_cv2:.4f}")

            error = abs(empirical_cv2 - theoretical_cv2) / theoretical_cv2
            assert error < 0.10, f"Empirical CV² error too large for k={case['k']}"

    def test_erlang_k1_is_exponential(self):
        """Test that Erlang-1 equals Exponential"""
        rate = 10.0

        erlang = ErlangService(shape=1, rate=rate)

        # Mean should be 1/rate
        assert abs(erlang.mean() - 1/rate) < 1e-10

        # CV² should be 1 (exponential property)
        assert abs(erlang.coefficient_of_variation() - 1.0) < 1e-10

    def test_erlang_as_k_increases(self):
        """Test that as k→∞, CV²→0 (approaches deterministic)"""
        k_values = [1, 2, 4, 8, 16, 32, 64, 128]
        rate = 10.0

        cv_values = []
        for k in k_values:
            erlang = ErlangService(shape=k, rate=k*rate)  # Maintain mean
            cv_values.append(erlang.coefficient_of_variation())

        print("\nCV² as k increases:")
        for k, cv2 in zip(k_values, cv_values):
            print(f"  k={k:3d}: CV²={cv2:.6f}")

        # CV² should strictly decrease
        for i in range(len(cv_values) - 1):
            assert cv_values[i] > cv_values[i+1], \
                f"CV² should decrease: {cv_values[i]} > {cv_values[i+1]}"

        # Last CV² should be very small
        assert cv_values[-1] < 0.01, "CV² should approach 0 as k→∞"


class TestMEkNQueue:
    """Test M/Ek/N queue implementation"""

    def test_mekn_stability_check(self):
        """Test that M/Ek/N rejects unstable configurations"""
        with pytest.raises(ValueError, match="unstable"):
            # ρ = 200/(10*12) = 1.67 > 1 (unstable!)
            config = MEkNConfig(
                arrival_rate=200,  # Too high
                num_threads=10,
                service_rate=12,
                erlang_k=3,
                sim_duration=100,
                warmup_time=10
            )
            analytical = MEkNAnalytical(
                arrival_rate=200,
                num_threads=10,
                service_rate=12,
                erlang_k=3
            )

    def test_mekn_basic_simulation(self):
        """Test basic M/Ek/N simulation runs without error"""
        config = MEkNConfig(
            arrival_rate=80,
            num_threads=10,
            service_rate=10,
            erlang_k=3,
            sim_duration=1000,
            warmup_time=100,
            random_seed=42
        )

        metrics = run_mekn_simulation(config)
        stats = metrics.summary_statistics()

        # Should have collected metrics
        assert len(metrics.wait_times) > 0
        assert stats['mean_wait'] >= 0
        assert stats['mean_response'] > stats['mean_wait']

    def test_mekn_different_k_values(self):
        """Test M/Ek/N with different k values"""
        base_config = {
            'arrival_rate': 80,
            'num_threads': 10,
            'service_rate': 10,
            'sim_duration': 2000,
            'warmup_time': 200,
            'random_seed': 42
        }

        waiting_times = []

        for k in [1, 2, 4, 8]:
            config = MEkNConfig(**base_config, erlang_k=k)
            metrics = run_mekn_simulation(config)
            stats = metrics.summary_statistics()
            waiting_times.append(stats['mean_wait'])

        print("\nWaiting times for different k:")
        for k, wq in zip([1, 2, 4, 8], waiting_times):
            print(f"  k={k}: Wq={wq:.6f}")

        # Generally should decrease (allowing for some noise)
        # At least 2 out of 3 transitions should show decrease
        decreases = sum(1 for i in range(len(waiting_times)-1)
                       if waiting_times[i] > waiting_times[i+1])
        assert decreases >= 2, "Waiting time should generally decrease with k"


class TestMEkNAnalytical:
    """Test M/Ek/N analytical formulas"""

    def test_mekn_analytical_cv_squared(self):
        """Test analytical CV² = 1/k"""
        for k in [1, 2, 3, 4, 8]:
            analytical = MEkNAnalytical(
                arrival_rate=80,
                num_threads=10,
                service_rate=10,
                erlang_k=k
            )

            cv2 = analytical.coefficient_of_variation()
            expected_cv2 = 1.0 / k

            assert abs(cv2 - expected_cv2) < 1e-10, \
                f"CV² should be 1/{k} = {expected_cv2}"

    def test_mekn_waiting_time_formula(self):
        """Test Wq(M/Ek/N) = Wq(M/M/N) * (1 + 1/k)/2"""
        from src.analysis.analytical import MMNAnalytical

        arrival_rate = 80
        num_threads = 10
        service_rate = 10
        k = 3

        # M/M/N baseline
        mmn = MMNAnalytical(arrival_rate, num_threads, service_rate)
        wq_mmn = mmn.mean_waiting_time()

        # M/Ek/N
        mekn = MEkNAnalytical(arrival_rate, num_threads, service_rate, k)
        wq_mekn = mekn.mean_waiting_time()

        # Expected from formula
        expected_wq = wq_mmn * (1 + 1/k) / 2

        print(f"\nWaiting time formula check:")
        print(f"  Wq(M/M/N): {wq_mmn:.6f}")
        print(f"  Wq(M/E{k}/N): {wq_mekn:.6f}")
        print(f"  Expected: {expected_wq:.6f}")

        assert abs(wq_mekn - expected_wq) < 1e-10, \
            "Waiting time formula incorrect"

    def test_mekn_littles_law(self):
        """Test Little's Law: Lq = λ * Wq"""
        analytical = MEkNAnalytical(
            arrival_rate=100,
            num_threads=10,
            service_rate=12,
            erlang_k=3
        )

        wq = analytical.mean_waiting_time()
        lq = analytical.mean_queue_length()

        expected_lq = analytical.lambda_ * wq

        print(f"\nLittle's Law check:")
        print(f"  Wq: {wq:.6f}")
        print(f"  Lq: {lq:.6f}")
        print(f"  λ*Wq: {expected_lq:.6f}")

        assert abs(lq - expected_lq) < 1e-10, "Little's Law violated"

    def test_mekn_vs_simulation_accuracy(self):
        """Test analytical formulas match simulation"""
        config = MEkNConfig(
            arrival_rate=80,
            num_threads=10,
            service_rate=10,
            erlang_k=3,
            sim_duration=5000,
            warmup_time=500,
            random_seed=42
        )

        # Analytical
        analytical = MEkNAnalytical(
            arrival_rate=config.arrival_rate,
            num_threads=config.num_threads,
            service_rate=config.service_rate,
            erlang_k=config.erlang_k
        )

        # Simulation
        metrics = run_mekn_simulation(config)
        stats = metrics.summary_statistics()

        # Compare waiting time
        wq_analytical = analytical.mean_waiting_time()
        wq_simulated = stats['mean_wait']

        print(f"\nAnalytical vs Simulation:")
        print(f"  Wq(analytical): {wq_analytical:.6f}")
        print(f"  Wq(simulated):  {wq_simulated:.6f}")

        # Should be within 15%
        error = abs(wq_analytical - wq_simulated) / wq_simulated
        assert error < 0.15, f"Analytical error {error*100:.2f}% exceeds 15%"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
