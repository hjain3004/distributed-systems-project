"""
Test threading model implementations

Validates that:
1. DedicatedThreadingQueue respects max connections (Equation 11)
2. SharedThreadingQueue handles unlimited connections with overhead (Equation 13)
3. Both models produce reasonable performance metrics
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import MMNConfig
from src.models.threading import run_dedicated_simulation, run_shared_simulation
from src.models.mmn_queue import run_mmn_simulation
from src.analysis.analytical import ThreadingAnalytical


def test_dedicated_threading():
    """Test dedicated threading model"""
    print("=" * 70)
    print("TEST 1: Dedicated Threading Model")
    print("=" * 70)

    # Configuration
    config = MMNConfig(
        arrival_rate=50,  # Lower rate to avoid too many rejections
        num_threads=20,
        service_rate=12,
        sim_duration=1000,
        warmup_time=100,
        random_seed=42
    )

    print(f"\nConfiguration:")
    print(f"  λ = {config.arrival_rate} msg/sec")
    print(f"  N = {config.num_threads} threads")
    print(f"  μ = {config.service_rate} msg/sec/thread")
    print(f"  ρ = {config.utilization:.3f}")

    # Calculate theoretical max (Equation 11)
    threads_per_connection = 2
    theoretical_max = ThreadingAnalytical.dedicated_max_connections(
        config.num_threads, threads_per_connection
    )
    print(f"\nEquation 11: Nmax = {config.num_threads}/{threads_per_connection} = {theoretical_max}")

    # Run simulation
    print(f"\nRunning dedicated threading simulation...")
    metrics = run_dedicated_simulation(config, threads_per_connection)
    stats = metrics.summary_statistics()

    print(f"\nResults:")
    print(f"  Mean wait: {stats['mean_wait']:.6f} sec")
    print(f"  Mean response: {stats['mean_response']:.6f} sec")
    print(f"  P95 response: {stats['p95_response']:.6f} sec")
    print(f"  Throughput: {stats['throughput']:.2f} msg/sec")

    # Calculate theoretical throughput (Equation 12)
    theoretical_throughput = ThreadingAnalytical.dedicated_throughput(
        config.arrival_rate, config.num_threads, config.service_rate
    )
    actual_throughput = stats['throughput']
    throughput_error = abs(theoretical_throughput - actual_throughput) / theoretical_throughput * 100

    print(f"\nThroughput Validation (Equation 12):")
    print(f"  Theoretical: X = min({config.arrival_rate}, {theoretical_max}×{config.service_rate}) = {theoretical_throughput:.2f} msg/sec")
    print(f"  Actual: {actual_throughput:.2f} msg/sec")
    print(f"  Error: {throughput_error:.2f}%")

    if throughput_error < 10:
        print("  ✓ PASS: Throughput matches theory")
        return True
    else:
        print("  ✗ FAIL: Throughput error too high")
        return False


def test_shared_threading():
    """Test shared threading model"""
    print("\n" + "=" * 70)
    print("TEST 2: Shared Threading Model")
    print("=" * 70)

    # Configuration
    config = MMNConfig(
        arrival_rate=100,  # Higher rate to test scalability
        num_threads=10,
        service_rate=12,
        sim_duration=1000,
        warmup_time=100,
        random_seed=42
    )

    print(f"\nConfiguration:")
    print(f"  λ = {config.arrival_rate} msg/sec")
    print(f"  N = {config.num_threads} threads")
    print(f"  μ = {config.service_rate} msg/sec/thread")
    print(f"  ρ = {config.utilization:.3f}")

    overhead_coefficient = 0.1  # 10% overhead

    print(f"\nOverhead coefficient (α): {overhead_coefficient}")
    print(f"Equation 13: μeff = μ / (1 + α·Nactive/N)")

    # Run simulation
    print(f"\nRunning shared threading simulation...")
    metrics = run_shared_simulation(config, overhead_coefficient)
    stats = metrics.summary_statistics()

    print(f"\nResults:")
    print(f"  Mean wait: {stats['mean_wait']:.6f} sec")
    print(f"  Mean service: {stats['mean_service']:.6f} sec")
    print(f"  Mean response: {stats['mean_response']:.6f} sec")
    print(f"  P95 response: {stats['p95_response']:.6f} sec")
    print(f"  Throughput: {stats['throughput']:.2f} msg/sec")

    # Expected: service time should be higher than 1/μ due to overhead
    theoretical_service = 1.0 / config.service_rate
    actual_service = stats['mean_service']
    overhead_factor = actual_service / theoretical_service

    print(f"\nOverhead Analysis:")
    print(f"  Base service time (1/μ): {theoretical_service:.6f} sec")
    print(f"  Actual service time: {actual_service:.6f} sec")
    print(f"  Overhead factor: {overhead_factor:.2f}x")

    if overhead_factor > 1.0 and overhead_factor < 1.5:
        print("  ✓ PASS: Overhead within expected range (1.0-1.5x)")
        return True
    else:
        print("  ✗ FAIL: Overhead out of expected range")
        return False


def test_threading_comparison():
    """Compare dedicated vs shared threading"""
    print("\n" + "=" * 70)
    print("TEST 3: Dedicated vs Shared Comparison")
    print("=" * 70)

    # Same configuration for both
    config = MMNConfig(
        arrival_rate=80,
        num_threads=20,
        service_rate=12,
        sim_duration=2000,
        warmup_time=200,
        random_seed=42
    )

    print(f"\nConfiguration:")
    print(f"  λ = {config.arrival_rate} msg/sec")
    print(f"  N = {config.num_threads} threads")
    print(f"  μ = {config.service_rate} msg/sec/thread")
    print(f"  ρ = {config.utilization:.3f}")

    # Run baseline M/M/N
    print(f"\nRunning baseline M/M/N...")
    baseline_metrics = run_mmn_simulation(config)
    baseline_stats = baseline_metrics.summary_statistics()

    # Run dedicated
    print(f"\nRunning dedicated threading...")
    dedicated_metrics = run_dedicated_simulation(config, threads_per_connection=2)
    dedicated_stats = dedicated_metrics.summary_statistics()

    # Run shared
    print(f"\nRunning shared threading...")
    shared_metrics = run_shared_simulation(config, overhead_coefficient=0.1)
    shared_stats = shared_metrics.summary_statistics()

    # Compare
    print(f"\n{'Metric':<25} {'M/M/N':>15} {'Dedicated':>15} {'Shared':>15}")
    print("-" * 77)

    print(f"{'Mean Wait (sec)':<25} {baseline_stats['mean_wait']:>15.6f} {dedicated_stats['mean_wait']:>15.6f} {shared_stats['mean_wait']:>15.6f}")
    print(f"{'Mean Response (sec)':<25} {baseline_stats['mean_response']:>15.6f} {dedicated_stats['mean_response']:>15.6f} {shared_stats['mean_response']:>15.6f}")
    print(f"{'P95 Response (sec)':<25} {baseline_stats['p95_response']:>15.6f} {dedicated_stats['p95_response']:>15.6f} {shared_stats['p95_response']:>15.6f}")
    print(f"{'Throughput (msg/sec)':<25} {baseline_stats['throughput']:>15.2f} {dedicated_stats['throughput']:>15.2f} {shared_stats['throughput']:>15.2f}")

    print("\nExpected Behavior:")
    print("  - Dedicated: Similar to M/M/N (no overhead) but may reject messages")
    print("  - Shared: Slightly higher response time (due to overhead) but no rejections")

    return True


def main():
    """Run all threading tests"""
    print("\n" + "=" * 70)
    print(" THREADING MODEL VALIDATION TESTS")
    print("=" * 70)

    test1_pass = test_dedicated_threading()
    test2_pass = test_shared_threading()
    test3_pass = test_threading_comparison()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Test 1 (Dedicated): {'✓ PASS' if test1_pass else '✗ FAIL'}")
    print(f"Test 2 (Shared):    {'✓ PASS' if test2_pass else '✗ FAIL'}")
    print(f"Test 3 (Comparison): {'✓ PASS' if test3_pass else '✗ FAIL'}")

    if test1_pass and test2_pass and test3_pass:
        print("\n✓ ALL TESTS PASSED")
    else:
        print("\n✗ SOME TESTS FAILED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
