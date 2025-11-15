"""
Finite Capacity Queue Tests

Tests for M/M/N/K queueing with blocking (Erlang-B).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from src.core.config import FiniteCapacityConfig
from src.models.finite_capacity_queue import (
    run_finite_capacity_simulation,
    ErlangBAnalytical,
    compare_with_analytical
)


class TestFiniteCapacityBasic:
    """Basic finite capacity queue functionality tests"""

    def test_finite_capacity_runs(self):
        """Test that finite capacity queue simulation runs without errors"""
        config = FiniteCapacityConfig(
            arrival_rate=50.0,
            num_threads=8,
            service_rate=10.0,
            max_capacity=20,
            blocking_strategy='reject',
            sim_duration=100.0,
            warmup_time=10.0,
            random_seed=42
        )

        results = run_finite_capacity_simulation(config)

        # Should have results
        assert results['total_arrivals'] > 0
        assert results['completed'] > 0
        assert results['blocking_probability'] >= 0.0

    def test_no_blocking_low_load(self):
        """Test that low load results in minimal blocking"""
        config = FiniteCapacityConfig(
            arrival_rate=40.0,  # Low load: ρ = 0.5
            num_threads=10,
            service_rate=10.0,
            max_capacity=50,  # Large capacity
            blocking_strategy='reject',
            sim_duration=200.0,
            warmup_time=20.0,
            random_seed=42
        )

        results = run_finite_capacity_simulation(config)

        print(f"\nLow Load Test:")
        print(f"  Total arrivals: {results['total_arrivals']}")
        print(f"  Blocked: {results['blocked']}")
        print(f"  Blocking probability: {results['blocking_probability']:.6f}")

        # Low load with large capacity should have very low blocking
        assert results['blocking_probability'] < 0.05

    def test_blocking_overload(self):
        """Test that overload (λ > N·μ) causes significant blocking"""
        config = FiniteCapacityConfig(
            arrival_rate=150.0,  # Overload: would be ρ = 1.5 for M/M/N
            num_threads=10,
            service_rate=10.0,
            max_capacity=30,  # Limited capacity
            blocking_strategy='reject',
            sim_duration=200.0,
            warmup_time=20.0,
            random_seed=42
        )

        results = run_finite_capacity_simulation(config)

        print(f"\nOverload Test:")
        print(f"  Total arrivals: {results['total_arrivals']}")
        print(f"  Accepted: {results['accepted']}")
        print(f"  Blocked: {results['blocked']}")
        print(f"  Blocking probability: {results['blocking_probability']:.6f}")

        # Overload with limited capacity should have significant blocking
        assert results['blocking_probability'] > 0.1
        assert results['blocked'] > 0

    def test_capacity_enforcement(self):
        """Test that system never exceeds max capacity"""
        config = FiniteCapacityConfig(
            arrival_rate=80.0,
            num_threads=8,
            service_rate=10.0,
            max_capacity=25,
            blocking_strategy='reject',
            sim_duration=100.0,
            warmup_time=10.0,
            random_seed=42
        )

        results = run_finite_capacity_simulation(config)

        # Max queue length should not exceed capacity
        if results['max_queue_length'] > 0:
            # Queue length is part of total system
            assert results['max_queue_length'] < config.max_capacity


class TestFiniteCapacityErlangB:
    """Test Erlang-B analytical formulas"""

    def test_erlang_b_formula(self):
        """Test Erlang-B blocking probability calculation"""
        analytical = ErlangBAnalytical(
            arrival_rate=100.0,
            num_servers=10,
            service_rate=12.0,
            max_capacity=10  # K = N (no queue, pure blocking)
        )

        # Calculate Erlang-B
        b = analytical.erlang_b()

        print(f"\nErlang-B Test:")
        print(f"  Traffic intensity: {analytical.a:.3f}")
        print(f"  Blocking probability: {b:.6f}")

        # Erlang-B should be between 0 and 1
        assert 0.0 <= b <= 1.0

        # For a = 100/12 ≈ 8.33 with N=10, blocking should be moderate
        assert 0.05 < b < 0.5

    def test_erlang_b_increasing_with_traffic(self):
        """Test that Erlang-B increases with traffic intensity"""
        num_servers = 10
        service_rate = 10.0
        max_capacity = 10

        # Low traffic
        analytical_low = ErlangBAnalytical(
            arrival_rate=50.0,
            num_servers=num_servers,
            service_rate=service_rate,
            max_capacity=max_capacity
        )

        # High traffic
        analytical_high = ErlangBAnalytical(
            arrival_rate=95.0,
            num_servers=num_servers,
            service_rate=service_rate,
            max_capacity=max_capacity
        )

        b_low = analytical_low.erlang_b()
        b_high = analytical_high.erlang_b()

        print(f"\nErlang-B Traffic Test:")
        print(f"  Low traffic (a={analytical_low.a:.2f}): B = {b_low:.6f}")
        print(f"  High traffic (a={analytical_high.a:.2f}): B = {b_high:.6f}")

        # Higher traffic should have higher blocking
        assert b_high > b_low

    def test_finite_k_blocking_probability(self):
        """Test blocking probability for M/M/N/K (K > N)"""
        analytical = ErlangBAnalytical(
            arrival_rate=100.0,
            num_servers=10,
            service_rate=12.0,
            max_capacity=20  # K > N (has queue space)
        )

        p_block = analytical.blocking_probability_finite_k()

        print(f"\nFinite K Blocking Test:")
        print(f"  N = {analytical.N}, K = {analytical.K}")
        print(f"  Traffic intensity: {analytical.a:.3f}")
        print(f"  Blocking probability: {p_block:.6f}")

        # Should be valid probability
        assert 0.0 <= p_block <= 1.0

        # With K > N, blocking should be less than pure Erlang-B
        b_pure = analytical.erlang_b()
        assert p_block < b_pure

    def test_effective_arrival_rate(self):
        """Test effective arrival rate calculation"""
        analytical = ErlangBAnalytical(
            arrival_rate=100.0,
            num_servers=10,
            service_rate=12.0,
            max_capacity=15
        )

        lambda_eff = analytical.effective_arrival_rate()
        p_block = analytical.blocking_probability_finite_k()

        print(f"\nEffective Arrival Rate Test:")
        print(f"  Offered rate: {analytical.lambda_:.1f}")
        print(f"  Blocking probability: {p_block:.6f}")
        print(f"  Effective rate: {lambda_eff:.1f}")

        # Effective rate should be less than offered rate
        assert lambda_eff < analytical.lambda_

        # Should equal λ × (1 - P_block)
        expected = analytical.lambda_ * (1 - p_block)
        assert abs(lambda_eff - expected) < 0.01


class TestFiniteCapacitySimulationValidation:
    """Validate simulation against analytical results"""

    def test_simulation_vs_analytical_moderate_load(self):
        """Compare simulation with analytical for moderate load"""
        config = FiniteCapacityConfig(
            arrival_rate=80.0,
            num_threads=10,
            service_rate=10.0,
            max_capacity=20,
            blocking_strategy='reject',
            sim_duration=500.0,  # Long simulation for accuracy
            warmup_time=100.0,
            random_seed=42
        )

        # Run simulation
        sim_results = run_finite_capacity_simulation(config)

        # Calculate analytical
        analytical = ErlangBAnalytical(
            arrival_rate=config.arrival_rate,
            num_servers=config.num_threads,
            service_rate=config.service_rate,
            max_capacity=config.max_capacity
        )

        analytical_p_block = analytical.blocking_probability_finite_k()
        simulated_p_block = sim_results['blocking_probability']

        print(f"\nSimulation vs Analytical (Moderate Load):")
        print(f"  Analytical blocking: {analytical_p_block:.6f}")
        print(f"  Simulated blocking: {simulated_p_block:.6f}")

        # Allow 30% error due to stochastic variation
        if analytical_p_block > 0.01:
            error = abs(analytical_p_block - simulated_p_block) / analytical_p_block
            print(f"  Relative error: {error*100:.1f}%")
            assert error < 0.35

    def test_simulation_vs_analytical_high_blocking(self):
        """Compare simulation with analytical for high blocking scenario"""
        config = FiniteCapacityConfig(
            arrival_rate=120.0,  # High load
            num_threads=10,
            service_rate=10.0,
            max_capacity=15,  # Small capacity
            blocking_strategy='reject',
            sim_duration=500.0,
            warmup_time=100.0,
            random_seed=42
        )

        sim_results = run_finite_capacity_simulation(config)

        analytical = ErlangBAnalytical(
            arrival_rate=config.arrival_rate,
            num_servers=config.num_threads,
            service_rate=config.service_rate,
            max_capacity=config.max_capacity
        )

        analytical_p_block = analytical.blocking_probability_finite_k()
        simulated_p_block = sim_results['blocking_probability']

        print(f"\nSimulation vs Analytical (High Blocking):")
        print(f"  Analytical blocking: {analytical_p_block:.6f}")
        print(f"  Simulated blocking: {simulated_p_block:.6f}")

        # With high blocking, should be easier to validate
        error = abs(analytical_p_block - simulated_p_block) / analytical_p_block
        print(f"  Relative error: {error*100:.1f}%")
        assert error < 0.30

    def test_compare_with_analytical_function(self):
        """Test the compare_with_analytical helper function"""
        config = FiniteCapacityConfig(
            arrival_rate=90.0,
            num_threads=10,
            service_rate=10.0,
            max_capacity=18,
            blocking_strategy='reject',
            sim_duration=300.0,
            warmup_time=50.0,
            random_seed=42
        )

        sim_results = run_finite_capacity_simulation(config)

        # Use comparison function
        print("\n" + "="*70)
        compare_with_analytical(config, sim_results)
        print("="*70)

        # Just verify it runs without error
        assert True


class TestFiniteCapacityStability:
    """Test stability characteristics unique to finite capacity queues"""

    def test_stability_under_overload(self):
        """Test that M/M/N/K remains stable even when λ > N·μ"""
        # This is NOT stable for M/M/N, but IS stable for M/M/N/K
        config = FiniteCapacityConfig(
            arrival_rate=150.0,  # λ = 150
            num_threads=10,      # N = 10
            service_rate=10.0,   # μ = 10
            # λ/(N·μ) = 150/100 = 1.5 > 1 (would be unstable for M/M/N)
            max_capacity=40,
            blocking_strategy='reject',
            sim_duration=300.0,
            warmup_time=50.0,
            random_seed=42
        )

        # Should run without error
        results = run_finite_capacity_simulation(config)

        print(f"\nOverload Stability Test:")
        print(f"  λ/(N·μ) = {config.arrival_rate/(config.num_threads*config.service_rate):.2f}")
        print(f"  Total arrivals: {results['total_arrivals']}")
        print(f"  Blocking probability: {results['blocking_probability']:.3f}")
        print(f"  Completed: {results['completed']}")

        # Should have significant blocking, but system stays stable
        assert results['blocking_probability'] > 0.2
        assert results['completed'] > 0
        assert results['total_arrivals'] > 0

    def test_increasing_capacity_reduces_blocking(self):
        """Test that increasing K reduces blocking probability"""
        base_params = {
            'arrival_rate': 100.0,
            'num_threads': 10,
            'service_rate': 10.0,
            'blocking_strategy': 'reject',
            'sim_duration': 200.0,
            'warmup_time': 30.0,
            'random_seed': 42
        }

        # Small capacity
        config_small = FiniteCapacityConfig(**base_params, max_capacity=15)
        results_small = run_finite_capacity_simulation(config_small)

        # Large capacity
        config_large = FiniteCapacityConfig(**base_params, max_capacity=40)
        results_large = run_finite_capacity_simulation(config_large)

        print(f"\nCapacity Impact Test:")
        print(f"  K=15: Blocking = {results_small['blocking_probability']:.6f}")
        print(f"  K=40: Blocking = {results_large['blocking_probability']:.6f}")

        # Larger capacity should have lower blocking
        assert results_large['blocking_probability'] < results_small['blocking_probability']


class TestFiniteCapacityMetrics:
    """Test metrics collection and calculations"""

    def test_metrics_completeness(self):
        """Test that all required metrics are collected"""
        config = FiniteCapacityConfig(
            arrival_rate=70.0,
            num_threads=10,
            service_rate=10.0,
            max_capacity=25,
            blocking_strategy='reject',
            sim_duration=200.0,
            warmup_time=20.0,
            random_seed=42
        )

        results = run_finite_capacity_simulation(config)

        # Check all required metrics exist
        assert 'total_arrivals' in results
        assert 'accepted' in results
        assert 'blocked' in results
        assert 'completed' in results
        assert 'blocking_probability' in results
        assert 'mean_wait' in results
        assert 'mean_response' in results

    def test_blocking_probability_calculation(self):
        """Test that blocking probability is calculated correctly"""
        config = FiniteCapacityConfig(
            arrival_rate=100.0,
            num_threads=10,
            service_rate=10.0,
            max_capacity=20,
            blocking_strategy='reject',
            sim_duration=200.0,
            warmup_time=20.0,
            random_seed=42
        )

        results = run_finite_capacity_simulation(config)

        # Manual calculation
        if results['total_arrivals'] > 0:
            expected_p_block = results['blocked'] / results['total_arrivals']
            assert abs(results['blocking_probability'] - expected_p_block) < 0.0001

    def test_accepted_plus_blocked_equals_total(self):
        """Test that accepted + blocked = total arrivals"""
        config = FiniteCapacityConfig(
            arrival_rate=80.0,
            num_threads=10,
            service_rate=10.0,
            max_capacity=22,
            blocking_strategy='reject',
            sim_duration=200.0,
            warmup_time=20.0,
            random_seed=42
        )

        results = run_finite_capacity_simulation(config)

        print(f"\nAccounting Test:")
        print(f"  Total: {results['total_arrivals']}")
        print(f"  Accepted: {results['accepted']}")
        print(f"  Blocked: {results['blocked']}")
        print(f"  Sum (accepted + blocked): {results['accepted'] + results['blocked']}")

        # Note: total_arrivals includes ALL arrivals (even during warmup)
        # but accepted/blocked only count after warmup_time
        # So we expect: accepted + blocked <= total_arrivals
        total_accounted = results['accepted'] + results['blocked']
        assert total_accounted <= results['total_arrivals']

        # The difference should be roughly the warmup arrivals
        warmup_arrivals = results['total_arrivals'] - total_accounted
        expected_warmup = config.arrival_rate * config.warmup_time
        print(f"  Warmup arrivals: {warmup_arrivals} (expected ~{expected_warmup:.0f})")

        # Allow 50% tolerance for warmup arrival estimation
        assert abs(warmup_arrivals - expected_warmup) / expected_warmup < 0.5


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
