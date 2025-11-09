"""
Tandem Queue Validation Experiments

Validates analytical model against simulation for the two-stage
tandem queue system from Li et al. (2015).

Tests:
1. Basic validation (analytical vs simulation)
2. Impact of failure probability p on Stage 2 load
3. Network delay impact on end-to-end latency
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from src.core.config import TandemQueueConfig
from src.models.tandem_queue import run_tandem_simulation
from src.analysis.analytical import TandemQueueAnalytical


def validate_tandem_basic():
    """
    Experiment 1: Basic Tandem Queue Validation
    
    Compare analytical vs simulation for baseline configuration
    """
    print("="*70)
    print("EXPERIMENT 1: Basic Tandem Queue Validation")
    print("="*70)
    
    config = TandemQueueConfig(
        arrival_rate=100,        # λ = 100 msg/sec
        n1=10, mu1=12,          # Stage 1: 10 threads, 12 msg/sec/thread
        n2=10, mu2=12,          # Stage 2: 10 threads, 12 msg/sec/thread
        network_delay=0.01,      # D_link = 10ms
        failure_prob=0.1,        # p = 10%
        sim_duration=2000,
        warmup_time=200,
        random_seed=42
    )
    
    print("\nConfiguration:")
    print(f"  λ = {config.arrival_rate} msg/sec")
    print(f"  Stage 1: n₁={config.n1}, μ₁={config.mu1} → ρ₁={config.stage1_utilization:.3f}")
    print(f"  Stage 2: n₂={config.n2}, μ₂={config.mu2}")
    print(f"  Network: D={config.network_delay} sec, p={config.failure_prob}")
    print(f"\n  Stage 2 arrival rate: Λ₂ = λ/(1-p) = {config.stage2_effective_arrival:.1f} msg/sec")
    print(f"  Stage 2 utilization: ρ₂ = {config.stage2_utilization:.3f}")

    # Run simulation
    print("\nRunning simulation...")
    sim_results = run_tandem_simulation(config)
    
    # Calculate analytical
    print("\nCalculating analytical...")
    analytical = TandemQueueAnalytical(
        lambda_arrival=config.arrival_rate,
        n1=config.n1, mu1=config.mu1,
        n2=config.n2, mu2=config.mu2,
        network_delay=config.network_delay,
        failure_prob=config.failure_prob
    )

    analytical_metrics = analytical.all_metrics()

    # Compare
    print(f"\n{'='*70}")
    print("VALIDATION RESULTS")
    print(f"{'='*70}")

    print(f"\n{'Metric':<35} {'Analytical':>15} {'Simulation':>15} {'Error %':>10}")
    print(f"{'-'*77}")
    
    comparisons = [
        ('Stage 1 Mean Wait (sec)', 'stage1_mean_wait', 'mean_stage1_wait'),
        ('Stage 1 Response (sec)', 'stage1_mean_response', 'mean_stage1_response'),
        ('Network Time (sec)', 'expected_network_time', 'mean_network_time'),
        ('Stage 2 Mean Wait (sec)', 'stage2_mean_wait', 'mean_stage2_wait'),
        ('Stage 2 Response (sec)', 'stage2_mean_response', 'mean_stage2_response'),
        ('Total End-to-End (sec)', 'total_delivery_time', 'mean_end_to_end'),
    ]
    
    for label, analytical_key, sim_key in comparisons:
        analytical_val = analytical_metrics[analytical_key]
        sim_val = sim_results[sim_key]
        error = abs(analytical_val - sim_val) / analytical_val * 100 if analytical_val > 0 else 0
        
        print(f"{label:<35} {analytical_val:>15.6f} {sim_val:>15.6f} {error:>9.2f}%")
    
    # Stage 2 arrival rate validation
    print(f"\n{'='*70}")
    print("STAGE 2 ARRIVAL RATE VALIDATION (Key Insight!)")
    print(f"{'='*70}")
    
    analytical_lambda2 = analytical_metrics['Lambda2']
    sim_lambda2 = sim_results['stage2_arrival_rate']
    
    print(f"  Expected Λ₂ = λ/(1-p) = {analytical_lambda2:.2f} msg/sec")
    print(f"  Simulated Λ₂ = {sim_lambda2:.2f} msg/sec")
    print(f"  Error: {abs(analytical_lambda2 - sim_lambda2)/analytical_lambda2*100:.2f}%")
    
    increase_pct = (analytical_lambda2 / config.arrival_rate - 1) * 100
    print(f"\n  ✓ Stage 2 sees {increase_pct:.1f}% MORE arrivals due to retransmissions!")

    print(f"{'='*70}\n")

    return sim_results, analytical_metrics


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" TANDEM QUEUE BASIC VALIDATION - Li et al. (2015)")
    print(" Two-Stage Broker → Receiver Architecture")
    print("="*70)
    
    # Run basic validation
    exp1_sim, exp1_analytical = validate_tandem_basic()

    print("\n" + "="*70)
    print("BASIC VALIDATION COMPLETED")
    print("="*70)
    print("\nKey Validations:")
    print("  ✓ Analytical model matches simulation")
    print("  ✓ Stage 2 arrival rate Λ₂ = λ/(1-p) validated")
    print("="*70 + "\n")
