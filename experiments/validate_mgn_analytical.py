"""
Validate M/G/N analytical model against simulation

This experiment verifies that the M/G/N analytical formulas
(Pollaczek-Khinchine approximation) match simulation results
for different Pareto shape parameters.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from src.core.config import MGNConfig
from src.models.mgn_queue import run_mgn_simulation
from src.analysis.analytical import MGNAnalytical


def validate_mgn_model(alpha: float):
    """Validate M/G/N for a specific alpha value"""

    print(f"\n{'='*70}")
    print(f"Validating M/G/N with α = {alpha}")
    print(f"{'='*70}")

    # Configuration
    ARRIVAL_RATE = 100
    NUM_THREADS = 10
    SERVICE_RATE = 12

    config = MGNConfig(
        arrival_rate=ARRIVAL_RATE,
        num_threads=NUM_THREADS,
        service_rate=SERVICE_RATE,
        distribution="pareto",
        alpha=alpha,
        sim_duration=2000,  # Longer simulation for better accuracy
        warmup_time=200,
        random_seed=42
    )

    print(f"\nConfiguration:")
    print(f"  λ = {config.arrival_rate} messages/sec")
    print(f"  N = {config.num_threads} threads")
    print(f"  μ = {config.service_rate} messages/sec/thread")
    print(f"  α = {alpha}")
    print(f"  k (scale) = {config.scale:.6f} (auto-calculated)")
    print(f"  E[S] = {config.mean_service_time:.6f} sec")
    print(f"  CV² = {config.coefficient_of_variation:.4f}")
    print(f"  ρ = {config.utilization:.3f}")

    # Run simulation
    print(f"\nRunning simulation...")
    metrics = run_mgn_simulation(config)
    sim_stats = metrics.summary_statistics()

    print(f"Simulation complete:")
    print(f"  Messages processed: {len(metrics.wait_times)}")
    print(f"  Mean wait: {sim_stats['mean_wait']:.6f} sec")
    print(f"  Mean response: {sim_stats['mean_response']:.6f} sec")

    # Calculate analytical
    print(f"\nCalculating analytical M/G/N...")
    analytical = MGNAnalytical(
        arrival_rate=config.arrival_rate,
        num_threads=config.num_threads,
        mean_service=config.mean_service_time,
        variance_service=config.variance_service_time
    )

    analytical_wq = analytical.mean_waiting_time_mgn()
    analytical_response = analytical_wq + config.mean_service_time

    print(f"Analytical M/G/N:")
    print(f"  Mean wait: {analytical_wq:.6f} sec")
    print(f"  Mean response: {analytical_response:.6f} sec")

    # Compare
    print(f"\n{'Metric':<30} {'Analytical':>15} {'Simulation':>15} {'Error %':>15}")
    print("-" * 77)

    # Mean waiting time
    wq_error = abs(analytical_wq - sim_stats['mean_wait']) / analytical_wq * 100 if analytical_wq > 0 else 0
    print(f"{'Mean Waiting Time (sec)':<30} {analytical_wq:>15.6f} {sim_stats['mean_wait']:>15.6f} {wq_error:>14.2f}%")

    # Mean response time
    r_error = abs(analytical_response - sim_stats['mean_response']) / analytical_response * 100 if analytical_response > 0 else 0
    print(f"{'Mean Response Time (sec)':<30} {analytical_response:>15.6f} {sim_stats['mean_response']:>15.6f} {r_error:>14.2f}%")

    # Check if passed
    passed = wq_error < 20.0 and r_error < 20.0  # 20% tolerance for M/G/N approximation

    if passed:
        print(f"\n✓ PASS: M/G/N analytical matches simulation within 20%")
    else:
        print(f"\n✗ FAIL: M/G/N analytical has significant errors")

    print("=" * 70)

    return {
        'alpha': alpha,
        'cv_squared': config.coefficient_of_variation,
        'analytical_wq': analytical_wq,
        'simulation_wq': sim_stats['mean_wait'],
        'wq_error': wq_error,
        'analytical_response': analytical_response,
        'simulation_response': sim_stats['mean_response'],
        'response_error': r_error,
        'passed': passed
    }


def main():
    """Run M/G/N validation for multiple alpha values"""

    print("\n" + "="*70)
    print(" M/G/N ANALYTICAL MODEL VALIDATION")
    print("="*70)

    # Test different alpha values
    alphas = [2.5, 3.0, 3.5]

    results = []
    for alpha in alphas:
        result = validate_mgn_model(alpha)
        results.append(result)

    # Summary table
    df = pd.DataFrame(results)

    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print("\nMean Waiting Time Comparison:")
    print(df[['alpha', 'cv_squared', 'analytical_wq', 'simulation_wq', 'wq_error']].to_string(index=False))

    print("\n\nMean Response Time Comparison:")
    print(df[['alpha', 'analytical_response', 'simulation_response', 'response_error']].to_string(index=False))

    # Overall result
    all_passed = all(df['passed'])

    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL VALIDATIONS PASSED")
        print("\nThe M/G/N analytical model (Pollaczek-Khinchine approximation)")
        print("accurately predicts simulation results within 20% error.")
    else:
        print("✗ SOME VALIDATIONS FAILED")
        print("\nThe M/G/N approximation may not be accurate for these parameters.")
        print("Note: M/G/N has no exact closed-form solution; we use approximations.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
