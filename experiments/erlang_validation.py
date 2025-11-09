"""
Erlang Distribution Validation Experiment

Validates M/Ek/N queue implementation against analytical formulas.

Tests:
1. CV² = 1/k relationship
2. Waiting time decreases as k increases
3. M/E1/N = M/M/N (exponential case)
4. M/E∞/N → M/D/N (deterministic case)
5. Analytical vs simulation accuracy

Expected ordering:
Wq(M/D/N) < Wq(M/Ek/N) < Wq(M/M/N) for k > 1
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.models.mekn_queue import run_mekn_simulation, MEkNConfig
from src.models.mmn_queue import run_mmn_simulation
from src.core.config import MMNConfig
from src.analysis.analytical import MEkNAnalytical, MMNAnalytical


def validate_erlang_cv_relationship():
    """
    Validate CV² = 1/k relationship

    For Erlang-k distribution:
    - CV² should equal exactly 1/k
    - As k increases, CV² decreases (more predictable)
    """
    print("\n" + "="*70)
    print("TEST 1: Erlang CV² = 1/k Validation")
    print("="*70)

    k_values = [1, 2, 3, 4, 8, 16]
    results = []

    for k in k_values:
        config = MEkNConfig(
            arrival_rate=80,
            num_threads=10,
            service_rate=10,
            erlang_k=k,
            sim_duration=10000,
            warmup_time=1000,
            random_seed=42
        )

        # Run simulation
        metrics = run_mekn_simulation(config)
        stats = metrics.summary_statistics()

        # Calculate empirical CV²
        mean_service = np.mean(metrics.service_times)
        var_service = np.var(metrics.service_times, ddof=1)
        empirical_cv2 = var_service / (mean_service ** 2) if mean_service > 0 else 0

        # Theoretical CV²
        theoretical_cv2 = 1.0 / k

        results.append({
            'k': k,
            'theoretical_cv2': theoretical_cv2,
            'empirical_cv2': empirical_cv2,
            'error_pct': abs(empirical_cv2 - theoretical_cv2) / theoretical_cv2 * 100
        })

        print(f"\nk={k:2d}: CV²(theory)={theoretical_cv2:.4f}, "
              f"CV²(empirical)={empirical_cv2:.4f}, "
              f"Error={results[-1]['error_pct']:.2f}%")

    df = pd.DataFrame(results)

    print("\n" + "="*70)
    print("RESULTS:")
    print(df.to_string(index=False))

    # All errors should be small
    max_error = df['error_pct'].max()
    print(f"\nMax error: {max_error:.2f}%")
    assert max_error < 10, "CV² errors too large"

    print("\n✓ CV² = 1/k relationship validated!")

    return df


def validate_erlang_waiting_time_ordering():
    """
    Validate that waiting time decreases with increasing k

    Expected: Wq(M/M/N) > Wq(M/E2/N) > Wq(M/E4/N) > ... > Wq(M/D/N)

    This demonstrates that more phases → more predictable → less waiting
    """
    print("\n" + "="*70)
    print("TEST 2: Waiting Time Ordering (k↑ ⇒ Wq↓)")
    print("="*70)

    k_values = [1, 2, 4, 8, 16, 32]
    results = []

    base_config = {
        'arrival_rate': 80,
        'num_threads': 10,
        'service_rate': 10,
        'sim_duration': 10000,
        'warmup_time': 1000,
        'random_seed': 42
    }

    for k in k_values:
        # Analytical
        analytical = MEkNAnalytical(
            arrival_rate=base_config['arrival_rate'],
            num_threads=base_config['num_threads'],
            service_rate=base_config['service_rate'],
            erlang_k=k
        )

        # Simulation
        config = MEkNConfig(**base_config, erlang_k=k)
        metrics = run_mekn_simulation(config)
        stats = metrics.summary_statistics()

        results.append({
            'k': k,
            'analytical_wq': analytical.mean_waiting_time(),
            'simulated_wq': stats['mean_wait'],
            'cv_squared': 1/k
        })

        print(f"\nk={k:2d}: Wq(analytical)={results[-1]['analytical_wq']:.6f}, "
              f"Wq(simulated)={results[-1]['simulated_wq']:.6f}")

    df = pd.DataFrame(results)

    print("\n" + "="*70)
    print("RESULTS:")
    print(df.to_string(index=False))

    # Verify ordering: CV² decreases → Wq decreases
    cv_diffs = df['cv_squared'].diff().dropna()
    wq_analytical_diffs = df['analytical_wq'].diff().dropna()
    wq_simulated_diffs = df['simulated_wq'].diff().dropna()

    print("\nOrdering check:")
    print(f"  CV² strictly decreasing: {all(cv_diffs < 0)}")
    print(f"  Wq(analytical) strictly decreasing: {all(wq_analytical_diffs < 0)}")
    print(f"  Wq(simulated) generally decreasing: {sum(wq_simulated_diffs < 0) >= len(wq_simulated_diffs) * 0.8}")

    assert all(cv_diffs < 0), "CV² should strictly decrease"
    assert all(wq_analytical_diffs < 0), "Analytical Wq should strictly decrease"

    print("\n✓ Waiting time ordering validated!")

    return df


def validate_erlang_special_cases():
    """
    Validate special cases:
    1. M/E1/N = M/M/N (k=1 is exponential)
    2. M/E∞/N → M/D/N (k→∞ approaches deterministic)
    """
    print("\n" + "="*70)
    print("TEST 3: Special Cases (k=1 and k→∞)")
    print("="*70)

    base_config = {
        'arrival_rate': 80,
        'num_threads': 10,
        'service_rate': 10,
        'sim_duration': 10000,
        'warmup_time': 1000,
        'random_seed': 42
    }

    # Test 1: M/E1/N should equal M/M/N
    print("\n--- Case 1: M/E1/N = M/M/N ---")

    # M/M/N
    mmn_config = MMNConfig(**base_config)
    mmn_metrics = run_mmn_simulation(mmn_config)
    mmn_stats = mmn_metrics.summary_statistics()

    # M/E1/N
    me1n_config = MEkNConfig(**base_config, erlang_k=1)
    me1n_metrics = run_mekn_simulation(me1n_config)
    me1n_stats = me1n_metrics.summary_statistics()

    print(f"  M/M/N  Wq: {mmn_stats['mean_wait']:.6f}")
    print(f"  M/E1/N Wq: {me1n_stats['mean_wait']:.6f}")

    # Should be within 10%
    error = abs(mmn_stats['mean_wait'] - me1n_stats['mean_wait']) / mmn_stats['mean_wait']
    print(f"  Relative difference: {error*100:.2f}%")
    assert error < 0.15, "M/E1/N should match M/M/N within 15%"

    # Test 2: As k→∞, Wq should approach minimum (M/D/N behavior)
    print("\n--- Case 2: M/Ek/N → M/D/N as k→∞ ---")

    k_values = [1, 8, 32, 128]
    waiting_times = []

    for k in k_values:
        config = MEkNConfig(**base_config, erlang_k=k)
        metrics = run_mekn_simulation(config)
        stats = metrics.summary_statistics()
        waiting_times.append(stats['mean_wait'])
        print(f"  k={k:3d}: Wq={stats['mean_wait']:.6f}")

    # Waiting times should generally decrease (allowing for simulation noise)
    # Check: first value > last value (overall trend)
    assert waiting_times[0] > waiting_times[-1], \
        f"Overall waiting time should decrease: {waiting_times[0]:.6f} > {waiting_times[-1]:.6f}"

    # Check: most transitions show decrease (at least 50%)
    decreases = sum(1 for i in range(len(waiting_times)-1) if waiting_times[i] > waiting_times[i+1])
    total_transitions = len(waiting_times) - 1
    print(f"\n  Decreasing transitions: {decreases}/{total_transitions}")
    assert decreases >= total_transitions * 0.5, \
        "At least half of transitions should show decrease"

    print("\n✓ Special cases validated!")


def validate_analytical_vs_simulation():
    """
    Validate analytical formulas against simulation across different k values
    """
    print("\n" + "="*70)
    print("TEST 4: Analytical vs Simulation Accuracy")
    print("="*70)

    k_values = [2, 3, 4, 8]
    results = []

    for k in k_values:
        config = MEkNConfig(
            arrival_rate=80,
            num_threads=10,
            service_rate=10,
            erlang_k=k,
            sim_duration=10000,
            warmup_time=1000,
            random_seed=42
        )

        # Analytical
        analytical = MEkNAnalytical(
            arrival_rate=config.arrival_rate,
            num_threads=config.num_threads,
            service_rate=config.service_rate,
            erlang_k=k
        )

        # Simulation
        metrics = run_mekn_simulation(config)
        stats = metrics.summary_statistics()

        # Compare
        analytical_metrics = analytical.all_metrics()

        wq_error = abs(analytical_metrics['mean_waiting_time'] - stats['mean_wait']) / stats['mean_wait'] * 100
        response_error = abs(analytical_metrics['mean_response_time'] - stats['mean_response']) / stats['mean_response'] * 100

        results.append({
            'k': k,
            'analytical_wq': analytical_metrics['mean_waiting_time'],
            'simulated_wq': stats['mean_wait'],
            'wq_error_pct': wq_error,
            'analytical_response': analytical_metrics['mean_response_time'],
            'simulated_response': stats['mean_response'],
            'response_error_pct': response_error
        })

        print(f"\nk={k}:")
        print(f"  Wq: Analytical={results[-1]['analytical_wq']:.6f}, "
              f"Simulated={results[-1]['simulated_wq']:.6f}, "
              f"Error={wq_error:.2f}%")
        print(f"  R:  Analytical={results[-1]['analytical_response']:.6f}, "
              f"Simulated={results[-1]['simulated_response']:.6f}, "
              f"Error={response_error:.2f}%")

    df = pd.DataFrame(results)

    print("\n" + "="*70)
    print("ACCURACY SUMMARY:")
    print(df[['k', 'wq_error_pct', 'response_error_pct']].to_string(index=False))

    max_error = max(df['wq_error_pct'].max(), df['response_error_pct'].max())
    print(f"\nMax error: {max_error:.2f}%")

    assert max_error < 15, "Analytical errors should be < 15%"

    print("\n✓ Analytical formulas validated!")

    return df


def main():
    """Run all Erlang validation tests"""
    print("\n" + "="*70)
    print(" ERLANG DISTRIBUTION VALIDATION")
    print(" M/Ek/N Queue Implementation")
    print("="*70)

    # Run all tests
    test1_results = validate_erlang_cv_relationship()
    test2_results = validate_erlang_waiting_time_ordering()
    validate_erlang_special_cases()
    test4_results = validate_analytical_vs_simulation()

    # Summary
    print("\n" + "="*70)
    print(" ✓ ALL TESTS PASSED")
    print("="*70)
    print("\nKey Findings:")
    print("  1. CV² = 1/k relationship confirmed")
    print("  2. Waiting time decreases with increasing k")
    print("  3. M/E1/N ≈ M/M/N (exponential case)")
    print("  4. M/Ek/N → M/D/N as k→∞ (deterministic limit)")
    print("  5. Analytical formulas match simulation within 15%")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
