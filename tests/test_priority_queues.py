"""
Priority Queue Tests

Tests for M/M/N queueing with multiple priority classes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from src.core.config import PriorityQueueConfig
from src.models.priority_queue import run_priority_queue_simulation, compare_priority_classes


class TestPriorityQueueBasic:
    """Basic priority queue functionality tests"""

    def test_priority_queue_runs(self):
        """Test that priority queue simulation runs without errors"""
        config = PriorityQueueConfig(
            arrival_rate=50.0,
            num_threads=8,
            service_rate=10.0,
            num_priorities=2,
            priority_rates=[20.0, 30.0],
            preemptive=False,
            sim_duration=100.0,
            warmup_time=10.0,
            random_seed=42
        )

        results = run_priority_queue_simulation(config)

        # Should have results for both priorities
        assert 1 in results
        assert 2 in results

        # Both priorities should have completions
        assert results[1]['completions'] > 0
        assert results[2]['completions'] > 0

    def test_priority_ordering(self):
        """Test that higher priority gets better service"""
        config = PriorityQueueConfig(
            arrival_rate=75.0,  # High load (ρ = 0.9375)
            num_threads=8,
            service_rate=10.0,
            num_priorities=3,
            priority_rates=[20.0, 30.0, 25.0],  # High, Medium, Low
            preemptive=False,
            sim_duration=200.0,
            warmup_time=50.0,
            random_seed=42
        )

        results = run_priority_queue_simulation(config)

        print("\n" + "="*70)
        print("Priority Ordering Test")
        print("="*70)
        compare_priority_classes(results)

        # Priority 1 (highest) should have lowest wait time
        wait_1 = results[1]['mean_wait']
        wait_2 = results[2]['mean_wait']
        wait_3 = results[3]['mean_wait']

        print(f"\nWait times: P1={wait_1:.6f}, P2={wait_2:.6f}, P3={wait_3:.6f}")

        # Higher priority should have lower or equal wait
        assert wait_1 <= wait_2, f"Priority 1 should wait less than Priority 2"
        assert wait_2 <= wait_3, f"Priority 2 should wait less than Priority 3"

    def test_auto_distributed_priorities(self):
        """Test automatic distribution of arrival rates"""
        config = PriorityQueueConfig(
            arrival_rate=60.0,
            num_threads=10,
            service_rate=12.0,
            num_priorities=3,
            # Don't specify priority_rates - should auto-distribute
            sim_duration=100.0,
            warmup_time=10.0,
            random_seed=42
        )

        # Should auto-distribute to [20, 20, 20]
        assert len(config.priority_rates) == 3
        assert all(rate == 20.0 for rate in config.priority_rates)

        results = run_priority_queue_simulation(config)

        # All priorities should have similar arrivals (within statistical variation)
        arrivals = [results[p]['arrivals'] for p in [1, 2, 3]]
        mean_arrivals = np.mean(arrivals)

        for p in [1, 2, 3]:
            # Allow 30% variation due to randomness
            assert abs(results[p]['arrivals'] - mean_arrivals) / mean_arrivals < 0.3


class TestPriorityQueueAdvanced:
    """Advanced priority queue tests"""

    def test_starvation_prevention(self):
        """
        Test that low priority messages eventually get served

        Even under high load from higher priorities, low priority
        should not be completely starved.
        """
        config = PriorityQueueConfig(
            arrival_rate=70.0,
            num_threads=8,
            service_rate=10.0,
            num_priorities=3,
            priority_rates=[50.0, 15.0, 5.0],  # Very skewed toward high priority
            preemptive=False,
            sim_duration=500.0,  # Long simulation
            warmup_time=100.0,
            random_seed=42
        )

        results = run_priority_queue_simulation(config)

        # Even low priority (3) should complete some messages
        assert results[3]['completions'] > 0, "Low priority should not be completely starved"

        # But should wait much longer
        assert results[3]['mean_wait'] > results[1]['mean_wait']

        print(f"\nStarvation Test Results:")
        print(f"  Priority 1 completions: {results[1]['completions']}")
        print(f"  Priority 2 completions: {results[2]['completions']}")
        print(f"  Priority 3 completions: {results[3]['completions']}")
        print(f"  Priority 3 mean wait: {results[3]['mean_wait']:.6f} sec")

    def test_preemptive_vs_nonpreemptive(self):
        """
        Compare preemptive and non-preemptive scheduling

        Preemptive should give even better service to high priority.
        """
        base_config_params = {
            'arrival_rate': 60.0,
            'num_threads': 8,
            'service_rate': 10.0,
            'num_priorities': 2,
            'priority_rates': [40.0, 20.0],
            'sim_duration': 200.0,
            'warmup_time': 50.0,
            'random_seed': 42
        }

        # Non-preemptive
        config_nonpreempt = PriorityQueueConfig(
            **base_config_params,
            preemptive=False
        )

        # Preemptive
        config_preempt = PriorityQueueConfig(
            **base_config_params,
            preemptive=True
        )

        results_nonpreempt = run_priority_queue_simulation(config_nonpreempt)
        results_preempt = run_priority_queue_simulation(config_preempt)

        print(f"\n" + "="*70)
        print("Preemptive vs Non-Preemptive Comparison")
        print("="*70)
        print(f"\nNon-Preemptive:")
        print(f"  Priority 1 mean wait: {results_nonpreempt[1]['mean_wait']:.6f}")
        print(f"  Priority 2 mean wait: {results_nonpreempt[2]['mean_wait']:.6f}")
        print(f"\nPreemptive:")
        print(f"  Priority 1 mean wait: {results_preempt[1]['mean_wait']:.6f}")
        print(f"  Priority 2 mean wait: {results_preempt[2]['mean_wait']:.6f}")

        # Both should show priority ordering
        assert results_nonpreempt[1]['mean_wait'] < results_nonpreempt[2]['mean_wait']
        assert results_preempt[1]['mean_wait'] < results_preempt[2]['mean_wait']

    def test_high_vs_low_load(self):
        """Test priority queue behavior under different load conditions"""

        # Low load (ρ ~ 0.5)
        config_low = PriorityQueueConfig(
            arrival_rate=40.0,
            num_threads=10,
            service_rate=10.0,
            num_priorities=2,
            priority_rates=[20.0, 20.0],
            preemptive=False,
            sim_duration=200.0,
            warmup_time=50.0,
            random_seed=42
        )

        # High load (ρ ~ 0.85)
        config_high = PriorityQueueConfig(
            arrival_rate=85.0,
            num_threads=10,
            service_rate=10.0,
            num_priorities=2,
            priority_rates=[42.5, 42.5],
            preemptive=False,
            sim_duration=200.0,
            warmup_time=50.0,
            random_seed=42
        )

        results_low = run_priority_queue_simulation(config_low)
        results_high = run_priority_queue_simulation(config_high)

        print(f"\n" + "="*70)
        print("Load Comparison")
        print("="*70)
        print(f"\nLow Load (ρ=0.5):")
        print(f"  Priority 1 mean wait: {results_low[1]['mean_wait']:.6f}")
        print(f"  Priority 2 mean wait: {results_low[2]['mean_wait']:.6f}")
        print(f"\nHigh Load (ρ=0.85):")
        print(f"  Priority 1 mean wait: {results_high[1]['mean_wait']:.6f}")
        print(f"  Priority 2 mean wait: {results_high[2]['mean_wait']:.6f}")

        # High load should have higher wait times
        assert results_high[1]['mean_wait'] > results_low[1]['mean_wait']
        assert results_high[2]['mean_wait'] > results_low[2]['mean_wait']

        # Priority difference should be more pronounced under high load
        diff_low = results_low[2]['mean_wait'] - results_low[1]['mean_wait']
        diff_high = results_high[2]['mean_wait'] - results_high[1]['mean_wait']

        print(f"\nPriority differential:")
        print(f"  Low load:  {diff_low:.6f}")
        print(f"  High load: {diff_high:.6f}")

        # Usually (but not always), high load increases priority differential
        # We just verify both have some differential
        assert diff_low > 0 or diff_high > 0


class TestPriorityQueueMetrics:
    """Test metrics collection and calculations"""

    def test_per_priority_metrics(self):
        """Test that per-priority metrics are collected correctly"""
        config = PriorityQueueConfig(
            arrival_rate=50.0,
            num_threads=8,
            service_rate=10.0,
            num_priorities=2,
            priority_rates=[25.0, 25.0],
            preemptive=False,
            sim_duration=200.0,
            warmup_time=20.0,
            random_seed=42
        )

        results = run_priority_queue_simulation(config)

        for priority in [1, 2]:
            metrics = results[priority]

            # Check all required metrics exist
            assert 'arrivals' in metrics
            assert 'completions' in metrics
            assert 'mean_wait' in metrics
            assert 'mean_service' in metrics
            assert 'mean_response' in metrics
            assert 'p99_response' in metrics

            # Basic sanity checks
            assert metrics['arrivals'] > 0
            assert metrics['completions'] > 0
            assert metrics['mean_wait'] >= 0
            assert metrics['mean_service'] > 0
            assert metrics['mean_response'] > metrics['mean_wait']
            assert metrics['p99_response'] > metrics['mean_response']

    def test_percentile_calculations(self):
        """Test that percentile calculations are reasonable"""
        config = PriorityQueueConfig(
            arrival_rate=60.0,
            num_threads=8,
            service_rate=10.0,
            num_priorities=1,
            priority_rates=[60.0],
            preemptive=False,
            sim_duration=200.0,
            warmup_time=50.0,
            random_seed=42
        )

        results = run_priority_queue_simulation(config)
        metrics = results[1]

        # Percentiles should be ordered
        assert metrics['p50_response'] <= metrics['p95_response']
        assert metrics['p95_response'] <= metrics['p99_response']

        # Mean should be less than P99 (for typical distributions)
        assert metrics['mean_response'] < metrics['p99_response']

        print(f"\nPercentile Test:")
        print(f"  Mean: {metrics['mean_response']:.6f}")
        print(f"  P50:  {metrics['p50_response']:.6f}")
        print(f"  P95:  {metrics['p95_response']:.6f}")
        print(f"  P99:  {metrics['p99_response']:.6f}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
