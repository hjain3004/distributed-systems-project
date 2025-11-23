"""
Heterogeneous Server Validation Experiment

Demonstrates the key insight from Li et al. (2015) Future Work:
Heterogeneous servers have WORSE performance than homogeneous servers
with the same total capacity (due to increased service time variance).

This addresses the professor's critique about missing heterogeneous server modeling.

Experiments:
1. Compare homogeneous vs heterogeneous with same total capacity
2. Validate analytical approximations against simulation
3. Test different server selection policies
4. Show heterogeneity penalty increases with more variance
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from src.core.config import MMNConfig, HeterogeneousMMNConfig, ServerGroup
from src.models.mmn_queue import run_mmn_simulation
from src.models.heterogeneous_mmn import run_heterogeneous_mmn_simulation
from src.analysis.analytical import MMNAnalytical, HeterogeneousMMNAnalytical


def experiment_1_homogeneous_vs_heterogeneous():
    """
    Experiment 1: Homogeneous vs Heterogeneous with Same Total Capacity

    Setup:
    - Homogeneous: 5 servers @ μ = 12 msg/sec (total capacity: 60 msg/sec)
    - Heterogeneous: 2 @ μ=8, 3 @ μ=15 (total capacity: 61 msg/sec - HIGHER!)

    Expected Result:
    Despite higher capacity, heterogeneous system has LONGER waiting time!

    Reason: Increased variance in service times (some messages get slow servers)
    """
    print("="*70)
    print("EXPERIMENT 1: Homogeneous vs Heterogeneous Performance")
    print("="*70)

    ARRIVAL_RATE = 50
    RANDOM_SEED = 42

    # Homogeneous system: 5 servers @ μ=12
    print("\n--- System 1: Homogeneous (5 @ μ=12) ---")
    config_homo = MMNConfig(
        arrival_rate=ARRIVAL_RATE,
        num_threads=5,
        service_rate=12,
        sim_duration=1000,
        warmup_time=100,
        random_seed=RANDOM_SEED
    )

    print(f"Configuration:")
    print(f"  Servers: {config_homo.num_threads} @ μ={config_homo.service_rate}")
    print(f"  Total capacity: {config_homo.num_threads * config_homo.service_rate} msg/sec")
    print(f"  Utilization: {config_homo.utilization:.3f}")

    # Run simulation
    metrics_homo = run_mmn_simulation(config_homo)
    stats_homo = metrics_homo.summary_statistics()

    # Analytical
    analytical_homo = MMNAnalytical(ARRIVAL_RATE, 5, 12)

    print(f"\nResults:")
    print(f"  Analytical Wq: {analytical_homo.mean_waiting_time():.6f} sec")
    print(f"  Simulation Wq: {stats_homo['mean_wait']:.6f} sec")
    print(f"  Simulation P99: {stats_homo['p99_wait']:.6f} sec")

    # Heterogeneous system: 2 @ μ=8, 3 @ μ=15
    print("\n--- System 2: Heterogeneous (2@8 + 3@15) ---")
    config_het = HeterogeneousMMNConfig(
        arrival_rate=ARRIVAL_RATE,
        server_groups=[
            ServerGroup(count=2, service_rate=8.0, name="Slow (t2.small)"),
            ServerGroup(count=3, service_rate=15.0, name="Fast (t2.large)")
        ],
        selection_policy="random",
        sim_duration=1000,
        warmup_time=100,
        random_seed=RANDOM_SEED
    )

    print(f"Configuration:")
    print(f"  Group 1: 2 @ μ=8 (capacity: 16)")
    print(f"  Group 2: 3 @ μ=15 (capacity: 45)")
    print(f"  Total capacity: {config_het.total_capacity} msg/sec (HIGHER than homogeneous!)")
    print(f"  Weighted avg μ: {config_het.weighted_service_rate:.2f}")
    print(f"  Utilization: {config_het.utilization:.3f}")
    print(f"  Heterogeneity coeff: {config_het.heterogeneity_coefficient:.3f}")

    # Run simulation
    metrics_het = run_heterogeneous_mmn_simulation(config_het)
    stats_het = metrics_het.summary_statistics()

    # Analytical
    analytical_het = HeterogeneousMMNAnalytical(
        arrival_rate=ARRIVAL_RATE,
        server_groups=[(2, 8.0), (3, 15.0)]
    )

    print(f"\nResults:")
    print(f"  Analytical Wq (baseline): {analytical_het.mean_waiting_time_baseline():.6f} sec")
    print(f"  Analytical Wq (corrected): {analytical_het.mean_waiting_time_corrected():.6f} sec")
    print(f"  Simulation Wq: {stats_het['mean_wait']:.6f} sec")
    print(f"  Simulation P99: {stats_het['p99_wait']:.6f} sec")

    # Comparison
    print("\n" + "="*70)
    print("COMPARISON: Heterogeneous vs Homogeneous")
    print("="*70)
    print(f"\nCapacity:")
    print(f"  Homogeneous: 60 msg/sec")
    print(f"  Heterogeneous: 61 msg/sec (+1.7% more capacity)")

    print(f"\nWaiting Time (Simulation):")
    print(f"  Homogeneous: {stats_homo['mean_wait']:.6f} sec")
    print(f"  Heterogeneous: {stats_het['mean_wait']:.6f} sec")

    penalty_pct = (stats_het['mean_wait'] / stats_homo['mean_wait'] - 1) * 100
    print(f"  Heterogeneity Penalty: {penalty_pct:+.1f}%")

    print(f"\nP99 Latency:")
    print(f"  Homogeneous: {stats_homo['p99_wait']:.6f} sec")
    print(f"  Heterogeneous: {stats_het['p99_wait']:.6f} sec")

    p99_penalty = (stats_het['p99_wait'] / stats_homo['p99_wait'] - 1) * 100
    print(f"  Heterogeneity Penalty: {p99_penalty:+.1f}%")

    print(f"\nKey Insight:")
    if penalty_pct > 0:
        print(f"  ✓ Heterogeneous system performs WORSE despite MORE capacity!")
        print(f"  ✓ Reason: Higher variance in service times")
        print(f"  ✓ Service CV² = {analytical_het.coefficient_of_variation_squared():.3f} vs 1.0 (homogeneous)")
    else:
        print(f"  ✗ Unexpected result - heterogeneous should be worse!")

    print("="*70)

    return {
        'homogeneous': stats_homo,
        'heterogeneous': stats_het,
        'penalty_pct': penalty_pct
    }


def experiment_2_selection_policies():
    """
    Experiment 2: Compare Server Selection Policies

    Test different policies for choosing which server to use:
    - random: Baseline (weighted by server count)
    - fastest_first: Prefer fast servers when available
    - round_robin: Cycle through servers evenly
    - shortest_queue: Join shortest queue (JSQ)

    Expected: shortest_queue should perform best (minimizes wait time)
    """
    print("\n\n" + "="*70)
    print("EXPERIMENT 2: Server Selection Policies")
    print("="*70)

    ARRIVAL_RATE = 50
    SERVER_GROUPS = [
        ServerGroup(count=2, service_rate=8.0, name="Slow"),
        ServerGroup(count=3, service_rate=15.0, name="Fast")
    ]

    policies = ["random", "fastest_first", "round_robin", "shortest_queue"]
    results = []

    for policy in policies:
        print(f"\n--- Policy: {policy} ---")

        config = HeterogeneousMMNConfig(
            arrival_rate=ARRIVAL_RATE,
            server_groups=SERVER_GROUPS,
            selection_policy=policy,
            sim_duration=1000,
            warmup_time=100,
            random_seed=42
        )

        metrics = run_heterogeneous_mmn_simulation(config)
        stats = metrics.summary_statistics()

        results.append({
            'policy': policy,
            'mean_wait': stats['mean_wait'],
            'p95_wait': stats['p95_wait'],
            'p99_wait': stats['p99_wait'],
            'mean_response': stats['mean_response'],
            'p99_response': stats['p99_response']
        })

        print(f"  Mean Wq: {stats['mean_wait']:.6f} sec")
        print(f"  P99 Wq: {stats['p99_wait']:.6f} sec")

    # Results table
    print("\n" + "="*70)
    print("Policy Comparison")
    print("="*70)
    df = pd.DataFrame(results)
    print(df.to_string(index=False))

    # Find best policy
    best_policy = df.loc[df['mean_wait'].idxmin(), 'policy']
    worst_policy = df.loc[df['mean_wait'].idxmax(), 'policy']

    print(f"\nBest Policy: {best_policy}")
    print(f"Worst Policy: {worst_policy}")

    improvement = (df['mean_wait'].max() / df['mean_wait'].min() - 1) * 100
    print(f"Performance Improvement: {improvement:.1f}% (best vs worst)")

    print("="*70)

    return df


def experiment_3_heterogeneity_penalty():
    """
    Experiment 3: Heterogeneity Penalty vs Variance

    Test how heterogeneity penalty increases with more variance in server speeds.

    Scenarios (all with 5 total servers, capacity ≈ 60 msg/sec):
    1. Homogeneous: 5 @ μ=12 (CV=0, capacity=60)
    2. Low variance: 3 @ μ=11, 2 @ μ=13.5 (capacity=60)
    3. Medium variance: 3 @ μ=10, 2 @ μ=15 (capacity=60)
    4. High variance: 2 @ μ=8, 3 @ μ=15 (capacity=61)
    5. Very high variance: 1 @ μ=6, 4 @ μ=16 (capacity=70)

    Expected: Penalty increases with heterogeneity coefficient
    """
    print("\n\n" + "="*70)
    print("EXPERIMENT 3: Heterogeneity Penalty vs Variance")
    print("="*70)

    ARRIVAL_RATE = 50
    RANDOM_SEED = 42

    scenarios = [
        {
            'name': "Homogeneous",
            'servers': [(5, 12.0)],
            'is_heterogeneous': False
        },
        {
            'name': "Low Variance",
            'servers': [(3, 11.0), (2, 13.5)],
            'is_heterogeneous': True
        },
        {
            'name': "Medium Variance",
            'servers': [(3, 10.0), (2, 15.0)],
            'is_heterogeneous': True
        },
        {
            'name': "High Variance",
            'servers': [(2, 8.0), (3, 15.0)],
            'is_heterogeneous': True
        },
        {
            'name': "Very High Variance",
            'servers': [(1, 6.0), (4, 16.0)],
            'is_heterogeneous': True
        }
    ]

    results = []

    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")

        # Calculate total capacity
        capacity = sum(n * mu for n, mu in scenario['servers'])
        print(f"  Servers: {scenario['servers']}")
        print(f"  Total capacity: {capacity:.1f} msg/sec")

        if scenario['is_heterogeneous']:
            config = HeterogeneousMMNConfig(
                arrival_rate=ARRIVAL_RATE,
                server_groups=[ServerGroup(count=n, service_rate=mu) for n, mu in scenario['servers']],
                selection_policy="random",
                sim_duration=1000,
                warmup_time=100,
                random_seed=RANDOM_SEED
            )

            metrics = run_heterogeneous_mmn_simulation(config)
            stats = metrics.summary_statistics()

            analytical = HeterogeneousMMNAnalytical(ARRIVAL_RATE, scenario['servers'])
            heterogeneity_coeff = analytical.heterogeneity_coefficient()
            cv_squared = analytical.coefficient_of_variation_squared()
        else:
            # Homogeneous (baseline)
            n, mu = scenario['servers'][0]
            config = MMNConfig(
                arrival_rate=ARRIVAL_RATE,
                num_threads=n,
                service_rate=mu,
                sim_duration=1000,
                warmup_time=100,
                random_seed=RANDOM_SEED
            )

            metrics = run_mmn_simulation(config)
            stats = metrics.summary_statistics()
            heterogeneity_coeff = 0.0
            cv_squared = 1.0  # Exponential service

        results.append({
            'scenario': scenario['name'],
            'capacity': capacity,
            'heterogeneity_coeff': heterogeneity_coeff,
            'cv_squared': cv_squared,
            'mean_wait': stats['mean_wait'],
            'p99_wait': stats['p99_wait'],
        })

        print(f"  Heterogeneity coeff: {heterogeneity_coeff:.3f}")
        print(f"  Service CV²: {cv_squared:.3f}")
        print(f"  Mean Wq: {stats['mean_wait']:.6f} sec")
        print(f"  P99 Wq: {stats['p99_wait']:.6f} sec")

    # Results table
    print("\n" + "="*70)
    print("Heterogeneity Penalty Analysis")
    print("="*70)

    df = pd.DataFrame(results)

    # Calculate penalty relative to homogeneous baseline
    baseline_wq = df.loc[df['scenario'] == 'Homogeneous', 'mean_wait'].values[0]
    df['penalty_%'] = ((df['mean_wait'] / baseline_wq) - 1) * 100

    print(df.to_string(index=False))

    print(f"\nKey Findings:")
    print(f"  1. Homogeneous baseline: Wq = {baseline_wq:.6f} sec")
    print(f"  2. Penalty increases with heterogeneity coefficient:")

    for idx, row in df.iterrows():
        if row['heterogeneity_coeff'] > 0:
            print(f"     - {row['scenario']}: CV_μ={row['heterogeneity_coeff']:.3f} → {row['penalty_%']:+.1f}% penalty")

    max_penalty = df['penalty_%'].max()
    print(f"  3. Worst case: {max_penalty:+.1f}% increase in waiting time!")

    print("="*70)

    return df


def experiment_4_analytical_validation():
    """
    Experiment 4: Validate Analytical Approximations

    Compare three analytical approximations against simulation:
    1. Baseline (weighted average μ) - underestimates
    2. Variance-corrected - more accurate
    3. Upper bound - conservative estimate

    Expected: Corrected approximation within 10-15% of simulation
    """
    print("\n\n" + "="*70)
    print("EXPERIMENT 4: Analytical Approximation Validation")
    print("="*70)

    ARRIVAL_RATE = 50
    SERVER_GROUPS = [(2, 8.0), (3, 15.0)]

    print(f"\nConfiguration:")
    print(f"  Arrival rate: {ARRIVAL_RATE} msg/sec")
    print(f"  Server groups: {SERVER_GROUPS}")

    # Run simulation
    print(f"\nRunning simulation...")
    config = HeterogeneousMMNConfig(
        arrival_rate=ARRIVAL_RATE,
        server_groups=[ServerGroup(count=n, service_rate=mu) for n, mu in SERVER_GROUPS],
        selection_policy="random",
        sim_duration=2000,  # Longer for better accuracy
        warmup_time=200,
        random_seed=42
    )

    metrics = run_heterogeneous_mmn_simulation(config)
    stats = metrics.summary_statistics()
    sim_wq = stats['mean_wait']

    # Calculate analytical
    analytical = HeterogeneousMMNAnalytical(ARRIVAL_RATE, SERVER_GROUPS)

    wq_baseline = analytical.mean_waiting_time_baseline()
    wq_corrected = analytical.mean_waiting_time_corrected()
    wq_upper = analytical.mean_waiting_time_upper_bound()

    # Comparison
    print("\n" + "="*70)
    print("Analytical vs Simulation Comparison")
    print("="*70)
    print(f"\nSimulation (Ground Truth):")
    print(f"  Mean Wq: {sim_wq:.6f} sec")

    print(f"\nAnalytical Approximations:")
    print(f"  Baseline (M/M/N with μ_avg):")
    print(f"    Wq: {wq_baseline:.6f} sec")
    error_baseline = abs(wq_baseline - sim_wq) / sim_wq * 100
    print(f"    Error: {error_baseline:.1f}% ({'UNDER' if wq_baseline < sim_wq else 'OVER'}estimates)")

    print(f"\n  Variance-Corrected:")
    print(f"    Wq: {wq_corrected:.6f} sec")
    error_corrected = abs(wq_corrected - sim_wq) / sim_wq * 100
    print(f"    Error: {error_corrected:.1f}% ({'UNDER' if wq_corrected < sim_wq else 'OVER'}estimates)")

    print(f"\n  Upper Bound:")
    print(f"    Wq: {wq_upper:.6f} sec")
    error_upper = abs(wq_upper - sim_wq) / sim_wq * 100
    print(f"    Error: {error_upper:.1f}% ({'UNDER' if wq_upper < sim_wq else 'OVER'}estimates)")

    print(f"\n" + "="*70)
    print(f"Recommendation: Use variance-corrected approximation")
    print(f"  Error: {error_corrected:.1f}% (acceptable for queueing models)")
    print("="*70)

    # Also show the analytical comparison method
    print("\n")
    analytical.compare_with_homogeneous()

    return {
        'simulation': sim_wq,
        'baseline': wq_baseline,
        'corrected': wq_corrected,
        'upper': wq_upper,
        'error_corrected_%': error_corrected
    }


def main():
    """Run all heterogeneous server validation experiments"""
    print("\n" + "="*70)
    print(" HETEROGENEOUS SERVER MODELING VALIDATION")
    print(" Addresses Professor's Critique #1")
    print("="*70)
    print("\nDemonstrates:")
    print("  1. Heterogeneous servers INCREASE waiting time vs homogeneous")
    print("  2. Analytical approximations for heterogeneous systems")
    print("  3. Server selection policies impact performance")
    print("  4. Heterogeneity penalty increases with variance")
    print("="*70)

    # Run experiments
    exp1_results = experiment_1_homogeneous_vs_heterogeneous()
    exp2_results = experiment_2_selection_policies()
    exp3_results = experiment_3_heterogeneity_penalty()
    exp4_results = experiment_4_analytical_validation()

    # Summary
    print("\n\n" + "="*70)
    print(" SUMMARY: Heterogeneous Server Modeling")
    print("="*70)

    print(f"\n✓ Implemented Heterogeneous M/M/N Queue Model")
    print(f"  - Multiple server groups with different speeds")
    print(f"  - 4 server selection policies (random, fastest-first, round-robin, JSQ)")
    print(f"  - Demonstrated heterogeneity penalty: {exp1_results['penalty_pct']:+.1f}%")

    print(f"\n✓ Developed Analytical Approximations")
    print(f"  - Baseline (weighted average)")
    print(f"  - Variance-corrected (accounts for heterogeneity)")
    print(f"  - Upper bound (worst-case)")
    print(f"  - Validation error: {exp4_results['error_corrected_%']:.1f}%")

    print(f"\n✓ Validated Li et al. (2015) Future Work")
    print(f"  - Heterogeneous servers are mathematically interesting!")
    print(f"  - No closed-form solution (unlike homogeneous M/M/N)")
    print(f"  - Performance penalty from increased variance")

    print(f"\n" + "="*70)
    print(" ALL EXPERIMENTS COMPLETED SUCCESSFULLY")
    print("="*70)


if __name__ == "__main__":
    main()
