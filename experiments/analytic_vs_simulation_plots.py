"""
Analytical vs Simulation Overlay Plots

Creates comparison visualizations showing:
1. M/M/N: Analytical formulas vs simulation (varying load)
2. M/G/N: Heavy-tail impact (varying α)
3. Tandem Queue: End-to-end latency validation

This demonstrates that simulations match analytical predictions.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict

from src.core.config import MMNConfig, MGNConfig, TandemQueueConfig
from src.models.mmn_queue import run_mmn_simulation
from src.models.mgn_queue import run_mgn_simulation
from src.models.tandem_queue import run_tandem_simulation
from src.analysis.analytical import MMNAnalytical, MGNAnalytical, TandemQueueAnalytical


def plot_mmn_validation():
    """
    Plot 1: M/M/N Analytical vs Simulation (varying utilization)

    Shows mean response time as ρ increases from 0.3 to 0.9
    """
    print("\n" + "="*70)
    print("Plot 1: M/M/N Analytical vs Simulation")
    print("="*70)

    # Test different utilizations
    num_threads = 10
    service_rate = 12
    utilizations = np.linspace(0.3, 0.9, 7)

    analytical_response = []
    simulation_response = []
    simulation_std = []

    for rho in utilizations:
        # Calculate arrival rate for this utilization
        arrival_rate = rho * num_threads * service_rate

        print(f"\n  Testing ρ = {rho:.2f} (λ = {arrival_rate:.1f})...")

        # Analytical prediction
        analytical = MMNAnalytical(arrival_rate, num_threads, service_rate)
        analytical_response.append(analytical.mean_response_time())

        # Simulation (run 5 replications)
        sim_results = []
        for rep in range(5):
            config = MMNConfig(
                arrival_rate=arrival_rate,
                num_threads=num_threads,
                service_rate=service_rate,
                sim_duration=2000,
                warmup_time=200,
                random_seed=1000 + rep
            )
            metrics = run_mmn_simulation(config)
            stats = metrics.summary_statistics()
            sim_results.append(stats['mean_response'])

        simulation_response.append(np.mean(sim_results))
        simulation_std.append(np.std(sim_results, ddof=1))

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot analytical (solid line)
    ax.plot(utilizations, analytical_response, 'b-', linewidth=2, label='Analytical (M/M/N)')

    # Plot simulation (points with error bars)
    ax.errorbar(utilizations, simulation_response, yerr=simulation_std,
                fmt='ro', markersize=8, capsize=5, label='Simulation')

    ax.set_xlabel('Utilization (ρ)', fontsize=12)
    ax.set_ylabel('Mean Response Time (sec)', fontsize=12)
    ax.set_title('M/M/N: Analytical vs Simulation Validation', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/plots/mmn_validation.png', dpi=300, bbox_inches='tight')
    print("\n  ✓ Saved: results/plots/mmn_validation.png")

    return fig


def plot_mgn_heavy_tail():
    """
    Plot 2: M/G/N Heavy-Tail Impact (varying α)

    Shows p99 response time for different Pareto α values
    Compares analytical approximation vs empirical p99 from simulation
    """
    print("\n" + "="*70)
    print("Plot 2: M/G/N Heavy-Tail Impact")
    print("="*70)

    # Test different Pareto α values
    alphas = [2.1, 2.5, 3.0, 3.5, 4.0]

    analytical_p99 = []
    simulation_p99 = []
    simulation_std = []

    # Fixed parameters
    arrival_rate = 100
    num_threads = 10
    service_rate = 12

    for alpha in alphas:
        print(f"\n  Testing α = {alpha:.1f}...")

        # Service time distribution parameters for Pareto
        # E[S] = 1/μ = 1/12
        # For Pareto: E[S] = x_m * α / (α - 1)
        mean_service = 1.0 / service_rate
        x_m = mean_service * (alpha - 1) / alpha

        # Var[S] for Pareto: x_m² * α / ((α-1)²(α-2))
        if alpha > 2:
            var_service = (x_m ** 2) * alpha / ((alpha - 1) ** 2 * (alpha - 2))
        else:
            var_service = float('inf')

        # Analytical prediction
        if alpha > 2 and var_service != float('inf'):
            analytical = MGNAnalytical(arrival_rate, num_threads, mean_service, var_service)
            analytical_p99.append(analytical.p99_response_time())
        else:
            analytical_p99.append(np.nan)

        # Simulation (run 5 replications)
        sim_results = []
        for rep in range(5):
            config = MGNConfig(
                arrival_rate=arrival_rate,
                num_threads=num_threads,
                service_rate=service_rate,
                distribution='pareto',
                alpha=alpha,
                sim_duration=2000,
                warmup_time=200,
                random_seed=1000 + rep
            )
            metrics = run_mgn_simulation(config)
            stats = metrics.summary_statistics()
            sim_results.append(stats['p99_response'])

        simulation_p99.append(np.mean(sim_results))
        simulation_std.append(np.std(sim_results, ddof=1))

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot analytical (dashed line - showing it's an approximation)
    ax.plot(alphas, analytical_p99, 'b--', linewidth=2,
            label='Analytical (Normal Approx - HEURISTIC)', alpha=0.7)

    # Plot simulation (solid line with points)
    ax.errorbar(alphas, simulation_p99, yerr=simulation_std,
                fmt='ro-', markersize=8, capsize=5, linewidth=2,
                label='Simulation (Empirical p99)')

    ax.set_xlabel('Pareto Shape Parameter (α)', fontsize=12)
    ax.set_ylabel('99th Percentile Response Time (sec)', fontsize=12)
    ax.set_title('M/G/N Heavy-Tail: Analytical vs Simulation\n' +
                 '(Note: Analytical p99 underestimates for heavy tails α < 3)',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # Add vertical line at α=3 (where heavy-tail effects become strong)
    ax.axvline(x=3.0, color='gray', linestyle=':', linewidth=1.5, alpha=0.5)
    ax.text(3.05, ax.get_ylim()[1] * 0.9, 'α=3\n(heavy tail threshold)',
            fontsize=9, color='gray')

    plt.tight_layout()
    plt.savefig('results/plots/mgn_heavy_tail.png', dpi=300, bbox_inches='tight')
    print("\n  ✓ Saved: results/plots/mgn_heavy_tail.png")

    return fig


def plot_tandem_queue_validation():
    """
    Plot 3: Tandem Queue End-to-End Latency (varying failure probability)

    Shows total message delivery time as network failure rate increases
    """
    print("\n" + "="*70)
    print("Plot 3: Tandem Queue Analytical vs Simulation")
    print("="*70)

    # Test different failure probabilities
    failure_probs = np.linspace(0.0, 0.4, 5)

    analytical_delivery = []
    simulation_delivery = []
    simulation_std = []

    # Fixed parameters
    arrival_rate = 100
    n1, mu1 = 10, 12
    n2, mu2 = 15, 12  # Extra capacity for Stage 2
    network_delay = 0.01

    for p in failure_probs:
        print(f"\n  Testing failure probability p = {p:.2f}...")

        # Analytical prediction
        analytical = TandemQueueAnalytical(
            lambda_arrival=arrival_rate,
            n1=n1, mu1=mu1,
            n2=n2, mu2=mu2,
            network_delay=network_delay,
            failure_prob=p
        )
        analytical_delivery.append(analytical.total_message_delivery_time())

        # Simulation (run 5 replications)
        sim_results = []
        for rep in range(5):
            config = TandemQueueConfig(
                arrival_rate=arrival_rate,
                n1=n1, mu1=mu1,
                n2=n2, mu2=mu2,
                network_delay=network_delay,
                failure_prob=p,
                sim_duration=2000,
                warmup_time=200,
                random_seed=1000 + rep
            )
            results = run_tandem_simulation(config)
            sim_results.append(results['mean_delivery_time'])

        simulation_delivery.append(np.mean(sim_results))
        simulation_std.append(np.std(sim_results, ddof=1))

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot analytical (solid line)
    ax.plot(failure_probs, analytical_delivery, 'b-', linewidth=2,
            label='Analytical (Tandem Queue)')

    # Plot simulation (points with error bars)
    ax.errorbar(failure_probs, simulation_delivery, yerr=simulation_std,
                fmt='ro', markersize=8, capsize=5, label='Simulation')

    ax.set_xlabel('Network Failure Probability (p)', fontsize=12)
    ax.set_ylabel('Mean End-to-End Delivery Time (sec)', fontsize=12)
    ax.set_title('Tandem Queue: Analytical vs Simulation Validation\n' +
                 'Shows impact of network failures on delivery time',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/plots/tandem_validation.png', dpi=300, bbox_inches='tight')
    print("\n  ✓ Saved: results/plots/tandem_validation.png")

    return fig


def plot_stage2_arrival_rate():
    """
    Plot 4: Stage 2 Arrival Rate Formula Validation

    Shows that Λ₂ = λ/(1-p) holds in simulation
    """
    print("\n" + "="*70)
    print("Plot 4: Stage 2 Arrival Rate Formula (Λ₂ = λ/(1-p))")
    print("="*70)

    # Test different failure probabilities
    failure_probs = np.linspace(0.05, 0.4, 8)
    arrival_rate = 100

    analytical_lambda2 = []
    simulation_lambda2 = []
    simulation_std = []

    # Fixed parameters
    n1, mu1 = 10, 12
    n2, mu2 = 20, 12  # High capacity for Stage 2
    network_delay = 0.01

    for p in failure_probs:
        print(f"\n  Testing p = {p:.2f}...")

        # Analytical formula
        analytical_lambda2.append(arrival_rate / (1 - p))

        # Simulation (run 5 replications)
        sim_results = []
        for rep in range(5):
            config = TandemQueueConfig(
                arrival_rate=arrival_rate,
                n1=n1, mu1=mu1,
                n2=n2, mu2=mu2,
                network_delay=network_delay,
                failure_prob=p,
                sim_duration=2000,
                warmup_time=200,
                random_seed=1000 + rep
            )
            results = run_tandem_simulation(config)
            sim_results.append(results['stage2_arrival_rate'])

        simulation_lambda2.append(np.mean(sim_results))
        simulation_std.append(np.std(sim_results, ddof=1))

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot analytical formula (solid line)
    ax.plot(failure_probs, analytical_lambda2, 'b-', linewidth=2,
            label='Analytical: Λ₂ = λ/(1-p)')

    # Plot simulation (points with error bars)
    ax.errorbar(failure_probs, simulation_lambda2, yerr=simulation_std,
                fmt='ro', markersize=8, capsize=5, label='Simulation')

    # Add horizontal line for λ
    ax.axhline(y=arrival_rate, color='gray', linestyle='--', linewidth=1,
               alpha=0.5, label=f'λ₁ = {arrival_rate}')

    ax.set_xlabel('Network Failure Probability (p)', fontsize=12)
    ax.set_ylabel('Stage 2 Arrival Rate (Λ₂)', fontsize=12)
    ax.set_title('Stage 2 Arrival Rate: Λ₂ = λ/(1-p) Validation\n' +
                 'Shows retransmissions increase Stage 2 load',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/plots/stage2_arrival_validation.png', dpi=300, bbox_inches='tight')
    print("\n  ✓ Saved: results/plots/stage2_arrival_validation.png")

    return fig


def main():
    """Generate all analytical vs simulation plots"""
    print("\n" + "="*70)
    print(" ANALYTICAL vs SIMULATION VALIDATION PLOTS")
    print(" Demonstrates simulation accuracy against theory")
    print("="*70)

    # Create output directory
    os.makedirs('results/plots', exist_ok=True)

    # Generate all plots
    try:
        plot_mmn_validation()
        plot_mgn_heavy_tail()
        plot_tandem_queue_validation()
        plot_stage2_arrival_rate()

        print("\n" + "="*70)
        print("✓ ALL VALIDATION PLOTS CREATED")
        print("="*70)
        print("\nPlots saved to results/plots/:")
        print("  1. mmn_validation.png - M/M/N analytical vs simulation")
        print("  2. mgn_heavy_tail.png - Heavy-tail impact on p99")
        print("  3. tandem_validation.png - End-to-end latency validation")
        print("  4. stage2_arrival_validation.png - Λ₂ = λ/(1-p) formula")
        print("\nThese plots demonstrate simulation accuracy and theoretical correctness.")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ Error generating plots: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
