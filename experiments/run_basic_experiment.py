"""
Basic experiment to validate M/M/N and M/G/N models

This script:
1. Runs M/M/N simulation
2. Compares with analytical results
3. Runs M/G/N with heavy-tail
4. Compares the two models
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from src.core.config import MMNConfig, MGNConfig
from src.models.mmn_queue import run_mmn_simulation
from src.models.mgn_queue import run_mgn_simulation
from src.analysis.analytical import MMNAnalytical, MGNAnalytical
from src.core.distributions import ParetoService


def experiment_1_mmn_validation():
    """Experiment 1: Validate M/M/N against analytical"""
    print("=" * 70)
    print("EXPERIMENT 1: M/M/N Baseline Validation")
    print("=" * 70)

    config = MMNConfig(
        arrival_rate=100,
        num_threads=10,
        service_rate=12,
        sim_duration=1000,
        warmup_time=100,
        random_seed=42
    )

    print(f"\nConfiguration:")
    print(f"  λ = {config.arrival_rate} messages/sec")
    print(f"  N = {config.num_threads} threads")
    print(f"  μ = {config.service_rate} messages/sec/thread")
    print(f"  ρ = {config.utilization:.3f}")

    # Run simulation
    print("\nRunning simulation...")
    metrics = run_mmn_simulation(config)
    sim_stats = metrics.summary_statistics()

    # Calculate analytical
    print("\nCalculating analytical results...")
    analytical = MMNAnalytical(
        arrival_rate=config.arrival_rate,
        num_threads=config.num_threads,
        service_rate=config.service_rate
    )
    analytical_metrics = analytical.all_metrics()

    # Compare
    print("\nResults Comparison:")
    print(f"{'Metric':<30} {'Analytical':>15} {'Simulation':>15} {'Error %':>15}")
    print("-" * 77)

    # Mean waiting time
    analytical_wq = analytical_metrics['mean_waiting_time']
    simulation_wq = sim_stats['mean_wait']
    error_wq = abs(analytical_wq - simulation_wq) / analytical_wq * 100 if analytical_wq > 0 else 0

    print(f"{'Mean Waiting Time (sec)':<30} {analytical_wq:>15.6f} {simulation_wq:>15.6f} {error_wq:>14.2f}%")

    # Mean queue length
    analytical_lq = analytical_metrics['mean_queue_length']
    simulation_lq = sim_stats['mean_queue_length']
    error_lq = abs(analytical_lq - simulation_lq) / analytical_lq * 100 if analytical_lq > 0 else 0

    print(f"{'Mean Queue Length':<30} {analytical_lq:>15.6f} {simulation_lq:>15.6f} {error_lq:>14.2f}%")

    # Mean response time
    analytical_r = analytical_metrics['mean_response_time']
    simulation_r = sim_stats['mean_response']
    error_r = abs(analytical_r - simulation_r) / analytical_r * 100 if analytical_r > 0 else 0

    print(f"{'Mean Response Time (sec)':<30} {analytical_r:>15.6f} {simulation_r:>15.6f} {error_r:>14.2f}%")

    print("\n" + "=" * 70)
    return sim_stats, analytical_metrics


def experiment_2_heavy_tail():
    """Experiment 2: M/G/N with heavy-tailed distribution"""
    print("\nEXPERIMENT 2: Heavy-Tailed Service Times (M/G/N)")
    print("=" * 70)

    # Fixed parameters
    ARRIVAL_RATE = 100
    NUM_THREADS = 10
    SERVICE_RATE = 12

    # Test different alpha values (Pareto shape parameter)
    alphas = [2.1, 2.5, 3.0]

    results = []

    for alpha in alphas:
        print(f"\n--- Testing α = {alpha} ---")

        config = MGNConfig(
            arrival_rate=ARRIVAL_RATE,
            num_threads=NUM_THREADS,
            service_rate=SERVICE_RATE,
            distribution="pareto",
            alpha=alpha,
            sim_duration=1000,
            warmup_time=100,
            random_seed=42
        )

        # Scale is now calculated automatically as a @property
        print(f"  Configuration: α={alpha}, scale={config.scale:.6f} (auto-calculated)")
        print(f"  Mean service time: {config.mean_service_time:.6f} sec")
        print(f"  CV²: {config.coefficient_of_variation:.2f}")

        # Run simulation
        metrics = run_mgn_simulation(config)
        stats = metrics.summary_statistics()

        results.append({
            'alpha': alpha,
            'cv_squared': config.coefficient_of_variation,
            'mean_wait': stats['mean_wait'],
            'p95_wait': stats['p95_wait'],
            'p99_wait': stats['p99_wait'],
            'mean_response': stats['mean_response'],
            'p99_response': stats['p99_response'],
        })

        print(f"  Mean wait: {stats['mean_wait']:.6f} sec")
        print(f"  P99 wait: {stats['p99_wait']:.6f} sec")

    # Display comparison table
    df = pd.DataFrame(results)
    print("\n" + "=" * 70)
    print("Heavy-Tail Impact Summary:")
    print("=" * 70)
    print(df.to_string(index=False))
    print("=" * 70)

    return df


def main():
    """Run all basic experiments"""
    print("\n" + "="*70)
    print(" MESSAGE BROKER PERFORMANCE MODELING")
    print(" Basic Validation Experiments")
    print("="*70)

    # Experiment 1: M/M/N validation
    sim_stats, analytical_metrics = experiment_1_mmn_validation()

    # Experiment 2: Heavy-tail comparison
    heavy_tail_results = experiment_2_heavy_tail()

    print("\n" + "="*70)
    print("ALL EXPERIMENTS COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nNext steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run full experiments: python experiments/run_all.py")
    print("  3. See PROJECT_PLAN.md for complete implementation details")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
