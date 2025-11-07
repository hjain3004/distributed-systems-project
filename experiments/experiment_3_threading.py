"""
Experiment 3: Threading Model Comparison

Compares three threading architectures:
1. M/M/N baseline (standard queue, no threading constraints)
2. Dedicated threading (thread-per-connection, limited connections)
3. Shared threading (worker pool, unlimited connections, overhead)

Tests across different load levels to demonstrate tradeoffs:
- Low load (ρ=0.5): All models should perform similarly
- Medium load (ρ=0.7): Dedicated starts rejecting connections
- High load (ρ=0.9): Clear performance/scalability tradeoffs
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from src.core.config import MMNConfig
from src.models.mmn_queue import run_mmn_simulation
from src.models.threading import run_dedicated_simulation, run_shared_simulation


def run_threading_comparison(arrival_rate: float, num_threads: int, service_rate: float):
    """Compare all three models at a specific load level"""

    config = MMNConfig(
        arrival_rate=arrival_rate,
        num_threads=num_threads,
        service_rate=service_rate,
        sim_duration=2000,
        warmup_time=200,
        random_seed=42
    )

    rho = config.utilization

    print(f"\n{'='*70}")
    print(f"Load: λ={arrival_rate}, N={num_threads}, μ={service_rate}, ρ={rho:.3f}")
    print(f"{'='*70}")

    # Run M/M/N baseline
    print(f"\n1. Running M/M/N baseline...")
    baseline_metrics = run_mmn_simulation(config)
    baseline_stats = baseline_metrics.summary_statistics()

    # Run dedicated threading
    print(f"\n2. Running dedicated threading...")
    dedicated_metrics = run_dedicated_simulation(config, threads_per_connection=2)
    dedicated_stats = dedicated_metrics.summary_statistics()

    # Calculate rejection info for dedicated
    # Note: The DedicatedThreadingQueue tracks rejected_count internally
    # We can infer it from the difference in processed messages

    # Run shared threading
    print(f"\n3. Running shared threading...")
    shared_metrics = run_shared_simulation(config, overhead_coefficient=0.1)
    shared_stats = shared_metrics.summary_statistics()

    return {
        'rho': rho,
        'arrival_rate': arrival_rate,
        'baseline_mean_wait': baseline_stats['mean_wait'],
        'baseline_mean_response': baseline_stats['mean_response'],
        'baseline_p95_response': baseline_stats['p95_response'],
        'baseline_throughput': baseline_stats['throughput'],
        'dedicated_mean_wait': dedicated_stats['mean_wait'],
        'dedicated_mean_response': dedicated_stats['mean_response'],
        'dedicated_p95_response': dedicated_stats['p95_response'],
        'dedicated_throughput': dedicated_stats['throughput'],
        'shared_mean_wait': shared_stats['mean_wait'],
        'shared_mean_response': shared_stats['mean_response'],
        'shared_p95_response': shared_stats['p95_response'],
        'shared_throughput': shared_stats['throughput'],
    }


def main():
    """Run comprehensive threading comparison"""

    print("\n" + "="*70)
    print(" EXPERIMENT 3: THREADING MODEL COMPARISON")
    print("="*70)

    # Fixed parameters
    NUM_THREADS = 20
    SERVICE_RATE = 12  # μ = 12 msg/sec/thread

    # Test different load levels
    # Total capacity = N × μ = 20 × 12 = 240 msg/sec
    load_configs = [
        {'rho': 0.5, 'lambda': 120},   # Light load
        {'rho': 0.6, 'lambda': 144},   # Medium-low
        {'rho': 0.7, 'lambda': 168},   # Medium
        {'rho': 0.8, 'lambda': 192},   # Medium-high
        {'rho': 0.9, 'lambda': 216},   # Heavy load
    ]

    results = []
    for config in load_configs:
        result = run_threading_comparison(
            arrival_rate=config['lambda'],
            num_threads=NUM_THREADS,
            service_rate=SERVICE_RATE
        )
        results.append(result)

    # Create comparison dataframe
    df = pd.DataFrame(results)

    # Display results
    print("\n" + "="*70)
    print("THREADING MODEL COMPARISON RESULTS")
    print("="*70)

    print("\n--- Mean Response Time (sec) ---")
    print(df[['rho', 'baseline_mean_response', 'dedicated_mean_response', 'shared_mean_response']].to_string(index=False))

    print("\n--- P95 Response Time (sec) ---")
    print(df[['rho', 'baseline_p95_response', 'dedicated_p95_response', 'shared_p95_response']].to_string(index=False))

    print("\n--- Throughput (msg/sec) ---")
    print(df[['rho', 'baseline_throughput', 'dedicated_throughput', 'shared_throughput']].to_string(index=False))

    # Calculate performance ratios
    print("\n--- Dedicated vs Baseline (Response Time Ratio) ---")
    df['dedicated_vs_baseline_response'] = df['dedicated_mean_response'] / df['baseline_mean_response']
    print(df[['rho', 'dedicated_vs_baseline_response']].to_string(index=False))

    print("\n--- Shared vs Baseline (Response Time Ratio) ---")
    df['shared_vs_baseline_response'] = df['shared_mean_response'] / df['baseline_mean_response']
    print(df[['rho', 'shared_vs_baseline_response']].to_string(index=False))

    # Save results
    output_file = 'experiment_3_threading_results.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Results saved to: {output_file}")

    # Summary
    print("\n" + "="*70)
    print("KEY FINDINGS")
    print("="*70)
    print("\n1. Dedicated Threading:")
    print("   - Pros: Low latency (no context switching overhead)")
    print("   - Cons: Limited max connections (Nmax = N/2)")
    print("   - Best for: Low-to-medium load where max connections is sufficient")

    print("\n2. Shared Threading:")
    print("   - Pros: Unlimited connections, better scalability")
    print("   - Cons: ~10% overhead from context switching")
    print("   - Best for: High load with many concurrent connections")

    print("\n3. Performance Tradeoff:")
    print("   - At low load (ρ<0.7): Dedicated = Shared ≈ Baseline")
    print("   - At high load (ρ>0.8): Dedicated may reject; Shared handles all with overhead")

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
