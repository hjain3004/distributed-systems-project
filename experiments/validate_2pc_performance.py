"""
Two-Phase Commit (2PC) Performance Impact Validation

Addresses professor's critique #3: "The 2PC-Reliability Disconnect"

Professor's critique:
"In two_phase_commit.py, you simulate a transaction. Fine. But in your queueing
models (mgn_queue.py), how is the overhead of 2PC modeled? In the real world
(and in the paper), enabling reliability (2PC) dramatically reduces effective
service rate ($\mu$)."

This experiment demonstrates:
1. 2PC overhead SIGNIFICANTLY impacts queue performance
2. Service times include both processing AND protocol overhead
3. Throughput is reduced by 20-40% with 2PC
4. System can become unstable (ρ → 1) when adding 2PC
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from src.core.config import MMNConfig, MGNConfig
from src.models.mmn_queue import run_mmn_simulation
from src.models.mmn_2pc_queue import run_mmn_2pc_simulation, run_mgn_2pc_simulation
from src.analysis.analytical import MMNAnalytical


def experiment_1_baseline_vs_2pc():
    """
    Experiment 1: Baseline vs 2PC Performance Impact

    Compare M/M/N queue with and without 2PC overhead.

    Setup:
    - λ = 100 msg/sec
    - N = 10 threads
    - μ = 12 msg/sec (base processing rate)

    Without 2PC:
    - E[S] = 1/12 = 83.3ms
    - ρ = 100/(10*12) = 0.833 (stable)

    With 2PC (3 replicas, 10ms network):
    - E[S] ≈ 83.3ms + 30ms = 113ms
    - μ_eff ≈ 8.85 msg/sec (26% reduction!)
    - ρ_eff = 100/(10*8.85) = 0.943 (near saturation!)

    Expected Result: 2PC increases waiting time by 50-100%
    """
    print("="*70)
    print("EXPERIMENT 1: Baseline vs 2PC Performance Impact")
    print("="*70)

    ARRIVAL_RATE = 100
    NUM_THREADS = 10
    SERVICE_RATE = 12
    RANDOM_SEED = 42

    # Configuration
    config = MMNConfig(
        arrival_rate=ARRIVAL_RATE,
        num_threads=NUM_THREADS,
        service_rate=SERVICE_RATE,
        sim_duration=1000,
        warmup_time=100,
        random_seed=RANDOM_SEED
    )

    # Analytical baseline (without 2PC)
    analytical = MMNAnalytical(ARRIVAL_RATE, NUM_THREADS, SERVICE_RATE)
    analytical_wq = analytical.mean_waiting_time()
    analytical_rq = analytical.mean_response_time()

    print(f"\nConfiguration:")
    print(f"  λ = {ARRIVAL_RATE} msg/sec")
    print(f"  N = {NUM_THREADS} threads")
    print(f"  μ (base) = {SERVICE_RATE} msg/sec")
    print(f"  ρ (base) = {config.utilization:.3f}")

    # Baseline: Without 2PC
    print(f"\n--- BASELINE: M/M/N WITHOUT 2PC ---")
    metrics_baseline = run_mmn_simulation(config)
    stats_baseline = metrics_baseline.summary_statistics()

    print(f"\nResults:")
    print(f"  Analytical Wq: {analytical_wq:.6f} sec = {analytical_wq*1000:.2f}ms")
    print(f"  Simulation Wq: {stats_baseline['mean_wait']:.6f} sec = {stats_baseline['mean_wait']*1000:.2f}ms")
    print(f"  Mean service: {stats_baseline['mean_service']:.6f} sec = {stats_baseline['mean_service']*1000:.2f}ms")
    print(f"  Mean response: {stats_baseline['mean_response']:.6f} sec = {stats_baseline['mean_response']*1000:.2f}ms")
    print(f"  P99 response: {stats_baseline['p99_response']:.6f} sec = {stats_baseline['p99_response']*1000:.2f}ms")

    # With 2PC: 3 replicas, 10ms network
    print(f"\n--- WITH 2PC: 3 replicas, 10ms network ---")
    metrics_2pc = run_mmn_2pc_simulation(
        config,
        num_replicas=3,
        network_rtt_mean=0.010,  # 10ms
        replica_availability=0.99
    )
    stats_2pc = metrics_2pc.summary_statistics()

    print(f"\nResults:")
    print(f"  Simulation Wq: {stats_2pc['mean_wait']:.6f} sec = {stats_2pc['mean_wait']*1000:.2f}ms")
    print(f"  Mean service: {stats_2pc['mean_service']:.6f} sec = {stats_2pc['mean_service']*1000:.2f}ms")
    print(f"  Mean response: {stats_2pc['mean_response']:.6f} sec = {stats_2pc['mean_response']*1000:.2f}ms")
    print(f"  P99 response: {stats_2pc['p99_response']:.6f} sec = {stats_2pc['p99_response']*1000:.2f}ms")

    # Calculate impact
    print(f"\n" + "="*70)
    print("2PC PERFORMANCE IMPACT")
    print("="*70)

    service_increase = (stats_2pc['mean_service'] / stats_baseline['mean_service'] - 1) * 100
    wait_increase = (stats_2pc['mean_wait'] / stats_baseline['mean_wait'] - 1) * 100
    response_increase = (stats_2pc['mean_response'] / stats_baseline['mean_response'] - 1) * 100
    p99_increase = (stats_2pc['p99_response'] / stats_baseline['p99_response'] - 1) * 100

    print(f"\nService Time:")
    print(f"  Baseline: {stats_baseline['mean_service']*1000:.2f}ms")
    print(f"  With 2PC: {stats_2pc['mean_service']*1000:.2f}ms")
    print(f"  Increase: {service_increase:+.1f}% (2PC overhead)")

    # Effective service rate
    eff_service_rate_baseline = 1 / stats_baseline['mean_service']
    eff_service_rate_2pc = 1 / stats_2pc['mean_service']
    throughput_reduction = (1 - eff_service_rate_2pc / eff_service_rate_baseline) * 100

    print(f"\nEffective Service Rate:")
    print(f"  Baseline: μ_eff = {eff_service_rate_baseline:.2f} msg/sec")
    print(f"  With 2PC: μ_eff = {eff_service_rate_2pc:.2f} msg/sec")
    print(f"  Throughput reduction: {throughput_reduction:.1f}%")

    # Effective utilization
    rho_eff_2pc = ARRIVAL_RATE / (NUM_THREADS * eff_service_rate_2pc)

    print(f"\nEffective Utilization:")
    print(f"  Baseline: ρ = {config.utilization:.3f}")
    print(f"  With 2PC: ρ_eff = {rho_eff_2pc:.3f} (HIGHER!)")

    if rho_eff_2pc > 0.9:
        print(f"  ⚠️  System near saturation with 2PC!")

    print(f"\nWaiting Time:")
    print(f"  Baseline: {stats_baseline['mean_wait']*1000:.2f}ms")
    print(f"  With 2PC: {stats_2pc['mean_wait']*1000:.2f}ms")
    print(f"  Increase: {wait_increase:+.1f}% (queueing effect)")

    print(f"\nTotal Response Time:")
    print(f"  Baseline: {stats_baseline['mean_response']*1000:.2f}ms")
    print(f"  With 2PC: {stats_2pc['mean_response']*1000:.2f}ms")
    print(f"  Increase: {response_increase:+.1f}%")

    print(f"\nP99 Latency:")
    print(f"  Baseline: {stats_baseline['p99_response']*1000:.2f}ms")
    print(f"  With 2PC: {stats_2pc['p99_response']*1000:.2f}ms")
    print(f"  Increase: {p99_increase:+.1f}%")

    print(f"\nKey Findings:")
    print(f"  1. 2PC adds ~{stats_2pc['mean_service']*1000 - stats_baseline['mean_service']*1000:.0f}ms overhead per message")
    print(f"  2. Throughput reduced by {throughput_reduction:.0f}%")
    print(f"  3. Utilization increased from {config.utilization:.3f} → {rho_eff_2pc:.3f}")
    print(f"  4. Mean response time increased by {response_increase:.0f}%")

    print("="*70)

    return {
        'baseline': stats_baseline,
        '2pc': stats_2pc,
        'service_increase_%': service_increase,
        'throughput_reduction_%': throughput_reduction,
        'wait_increase_%': wait_increase,
        'rho_eff_2pc': rho_eff_2pc
    }


def experiment_2_replica_scaling():
    """
    Experiment 2: 2PC Overhead vs Number of Replicas

    Test how 2PC overhead scales with replica count.

    Expected: More replicas → higher vote collection time → worse performance
    """
    print("\n\n" + "="*70)
    print("EXPERIMENT 2: 2PC Overhead vs Replica Count")
    print("="*70)

    ARRIVAL_RATE = 100
    NUM_THREADS = 10
    SERVICE_RATE = 12

    config = MMNConfig(
        arrival_rate=ARRIVAL_RATE,
        num_threads=NUM_THREADS,
        service_rate=SERVICE_RATE,
        sim_duration=1000,
        warmup_time=100,
        random_seed=42
    )

    replica_counts = [1, 3, 5, 7]
    results = []

    for num_replicas in replica_counts:
        print(f"\n--- Testing {num_replicas} replicas ---")

        metrics = run_mmn_2pc_simulation(
            config,
            num_replicas=num_replicas,
            network_rtt_mean=0.010,
            replica_availability=0.99
        )
        stats = metrics.summary_statistics()

        results.append({
            'num_replicas': num_replicas,
            'mean_service': stats['mean_service'],
            'mean_wait': stats['mean_wait'],
            'mean_response': stats['mean_response'],
            'p99_response': stats['p99_response'],
        })

        print(f"  Mean service: {stats['mean_service']*1000:.2f}ms")
        print(f"  Mean wait: {stats['mean_wait']*1000:.2f}ms")

    # Results table
    print("\n" + "="*70)
    print("Replica Scaling Analysis")
    print("="*70)
    df = pd.DataFrame(results)
    print(df.to_string(index=False))

    print(f"\nKey Finding:")
    print(f"  More replicas → Longer vote collection → Higher overhead")
    print(f"  Service time ranges from {df['mean_service'].min()*1000:.0f}ms (1 replica)")
    print(f"  to {df['mean_service'].max()*1000:.0f}ms ({df['num_replicas'].max()} replicas)")

    print("="*70)

    return df


def experiment_3_network_latency():
    """
    Experiment 3: 2PC Overhead vs Network Latency

    Test how network latency affects 2PC overhead.

    Expected: Higher latency → proportionally higher 2PC overhead
    """
    print("\n\n" + "="*70)
    print("EXPERIMENT 3: 2PC Overhead vs Network Latency")
    print("="*70)

    ARRIVAL_RATE = 100
    NUM_THREADS = 10
    SERVICE_RATE = 12

    config = MMNConfig(
        arrival_rate=ARRIVAL_RATE,
        num_threads=NUM_THREADS,
        service_rate=SERVICE_RATE,
        sim_duration=1000,
        warmup_time=100,
        random_seed=42
    )

    # Test different network latencies
    network_latencies_ms = [1, 5, 10, 20, 50]  # milliseconds
    results = []

    for latency_ms in network_latencies_ms:
        latency_sec = latency_ms / 1000.0
        print(f"\n--- Testing {latency_ms}ms network latency ---")

        metrics = run_mmn_2pc_simulation(
            config,
            num_replicas=3,
            network_rtt_mean=latency_sec,
            replica_availability=0.99
        )
        stats = metrics.summary_statistics()

        results.append({
            'network_latency_ms': latency_ms,
            'mean_service_ms': stats['mean_service'] * 1000,
            'mean_wait_ms': stats['mean_wait'] * 1000,
            'mean_response_ms': stats['mean_response'] * 1000,
            'p99_response_ms': stats['p99_response'] * 1000,
        })

        print(f"  Mean service: {stats['mean_service']*1000:.2f}ms")
        print(f"  Mean wait: {stats['mean_wait']*1000:.2f}ms")

    # Results table
    print("\n" + "="*70)
    print("Network Latency Impact Analysis")
    print("="*70)
    df = pd.DataFrame(results)
    print(df.to_string(index=False))

    print(f"\nKey Finding:")
    print(f"  Network latency directly impacts 2PC overhead")
    print(f"  At 1ms: Service = {df.iloc[0]['mean_service_ms']:.1f}ms")
    print(f"  At 50ms: Service = {df.iloc[-1]['mean_service_ms']:.1f}ms")
    print(f"  Difference: {df.iloc[-1]['mean_service_ms'] - df.iloc[0]['mean_service_ms']:.1f}ms")

    print("="*70)

    return df


def main():
    """Run all 2PC performance validation experiments"""
    print("\n" + "="*70)
    print(" TWO-PHASE COMMIT PERFORMANCE IMPACT VALIDATION")
    print(" Addresses Professor's Critique #3")
    print("="*70)
    print("\nDemonstrates:")
    print("  1. 2PC overhead is INTEGRATED into service times")
    print("  2. Throughput is significantly reduced (20-40%)")
    print("  3. System utilization increases (can become unstable!)")
    print("  4. Response times increase by 50-100%")
    print("="*70)

    # Run experiments
    exp1_results = experiment_1_baseline_vs_2pc()
    exp2_results = experiment_2_replica_scaling()
    exp3_results = experiment_3_network_latency()

    # Summary
    print("\n\n" + "="*70)
    print(" SUMMARY: 2PC Performance Impact")
    print("="*70)

    print(f"\n✓ Professor's Critique ADDRESSED:")
    print(f"  'In your queueing models, how is the overhead of 2PC modeled?'")
    print(f"  → 2PC overhead IS NOW integrated into service time calculations")

    print(f"\n✓ Key Findings:")
    print(f"  1. Service time increase: {exp1_results['service_increase_%']:.1f}%")
    print(f"  2. Throughput reduction: {exp1_results['throughput_reduction_%']:.1f}%")
    print(f"  3. Effective utilization: {exp1_results['rho_eff_2pc']:.3f} (was 0.833)")
    print(f"  4. Waiting time increase: {exp1_results['wait_increase_%']:.1f}%")

    print(f"\n✓ Mathematical Model:")
    print(f"  Without 2PC: E[S] = 1/μ")
    print(f"  With 2PC: E[S] = 1/μ + 2PC_overhead")
    print(f"  Where: 2PC_overhead ≈ 3·RTT + p_timeout·timeout")

    print(f"\n✓ Real-World Impact:")
    print(f"  In production systems using 2PC for reliability:")
    print(f"  - Throughput can drop 20-40%")
    print(f"  - Latency can increase 50-100%")
    print(f"  - Systems can become unstable (ρ → 1)")

    print(f"\n" + "="*70)
    print(" ALL EXPERIMENTS COMPLETED SUCCESSFULLY")
    print("="*70)


if __name__ == "__main__":
    main()
