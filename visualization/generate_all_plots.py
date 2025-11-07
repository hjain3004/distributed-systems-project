"""
Generate all publication-quality plots

Creates 5 figures:
1. M/M/N Validation (analytical vs simulation)
2. Heavy-Tail Impact (4 subplots)
3. Threading Comparison (4 subplots)
4. Load Testing (all models)
5. Confidence Intervals (with error bars)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec

from plot_config import (
    setup_plot_style, save_figure, add_grid,
    format_axis_labels, COLORS, LINESTYLES, MARKERS
)

from src.core.config import MMNConfig, MGNConfig
from src.models.mmn_queue import run_mmn_simulation
from src.models.mgn_queue import run_mgn_simulation
from src.models.threading import run_dedicated_simulation, run_shared_simulation
from src.analysis.analytical import MMNAnalytical, MGNAnalytical


def plot_1_mmn_validation():
    """
    Plot 1: M/M/N Validation - Analytical vs Simulation

    Bar chart comparing analytical and simulation results
    for mean wait time, mean queue length, and mean response time
    """
    print("\n" + "="*70)
    print("Generating Plot 1: M/M/N Validation")
    print("="*70)

    # Run experiment
    config = MMNConfig(
        arrival_rate=100,
        num_threads=10,
        service_rate=12,
        sim_duration=1000,
        warmup_time=100,
        random_seed=42
    )

    print("Running M/M/N simulation...")
    metrics = run_mmn_simulation(config)
    sim_stats = metrics.summary_statistics()

    print("Calculating analytical...")
    analytical = MMNAnalytical(100, 10, 12)
    analytical_metrics = analytical.all_metrics()

    # Prepare data
    metrics_data = {
        'Mean Waiting Time (sec)': [
            analytical_metrics['mean_waiting_time'],
            sim_stats['mean_wait']
        ],
        'Mean Queue Length': [
            analytical_metrics['mean_queue_length'],
            sim_stats['mean_queue_length']
        ],
        'Mean Response Time (sec)': [
            analytical_metrics['mean_response_time'],
            sim_stats['mean_response']
        ]
    }

    # Create figure
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    for idx, (metric_name, values) in enumerate(metrics_data.items()):
        ax = axes[idx]

        analytical_val, simulation_val = values
        error = abs(analytical_val - simulation_val) / analytical_val * 100

        # Bar positions
        x = np.arange(2)
        bars = ax.bar(x, values,
                     color=[COLORS['analytical'], COLORS['simulation']],
                     alpha=0.7,
                     edgecolor='black',
                     linewidth=1.5)

        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.4f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Add error annotation
        ax.text(0.5, max(values) * 1.15,
               f'Error: {error:.2f}%',
               ha='center', va='bottom',
               fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

        ax.set_xticks(x)
        ax.set_xticklabels(['Analytical', 'Simulation'], fontweight='bold')
        ax.set_ylabel(metric_name.split('(')[0].strip(), fontweight='bold')
        ax.set_title(metric_name, fontweight='bold', pad=10)
        add_grid(ax)

    fig.suptitle('M/M/N Model Validation: Analytical vs Simulation\n' +
                 r'$\lambda=100$ msg/sec, $N=10$ threads, $\mu=12$ msg/sec/thread, $\rho=0.833$',
                 fontsize=14, fontweight='bold', y=1.05)

    save_figure(fig, 'visualization/plot_1_mmn_validation')
    plt.close()

    return metrics_data


def plot_2_heavy_tail_impact():
    """
    Plot 2: Heavy-Tail Impact (4 subplots)

    - Subplot A: Mean wait time vs α
    - Subplot B: P99 latency vs α
    - Subplot C: CV² vs α
    - Subplot D: Response time CDF for different α
    """
    print("\n" + "="*70)
    print("Generating Plot 2: Heavy-Tail Impact")
    print("="*70)

    # Test alpha values
    alphas = [2.1, 2.3, 2.5, 2.7, 3.0, 3.5, 4.0]

    results = []
    all_response_times = {}

    for alpha in alphas:
        print(f"  Running α={alpha}...")

        config = MGNConfig(
            arrival_rate=100,
            num_threads=10,
            service_rate=12,
            distribution="pareto",
            alpha=alpha,
            sim_duration=1000,
            warmup_time=100,
            random_seed=42
        )

        metrics = run_mgn_simulation(config)
        stats = metrics.summary_statistics()

        # Store response times for CDF
        all_response_times[alpha] = np.array(metrics.wait_times) + np.array(metrics.service_times)

        results.append({
            'alpha': alpha,
            'cv_squared': config.coefficient_of_variation,
            'mean_wait': stats['mean_wait'],
            'p95_wait': stats['p95_wait'],
            'p99_wait': stats['p99_wait'],
            'mean_response': stats['mean_response'],
            'p99_response': stats['p99_response'],
        })

    df = pd.DataFrame(results)

    # Create 2x2 subplot
    fig = plt.figure(figsize=(12, 10))
    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    # Subplot A: Mean wait time vs α
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(df['alpha'], df['mean_wait'], marker='o', linewidth=2,
            color=COLORS['mgn_heavy'], markersize=8)
    format_axis_labels(ax1,
                      xlabel=r'Pareto Shape Parameter ($\alpha$)',
                      ylabel='Mean Waiting Time (sec)',
                      title='(A) Mean Wait Time vs $\\alpha$')
    add_grid(ax1)

    # Subplot B: P99 latency vs α
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(df['alpha'], df['p99_wait'], marker='s', linewidth=2,
            color=COLORS['mgn_medium'], markersize=8, label='P99 Wait')
    ax2.plot(df['alpha'], df['p99_response'], marker='^', linewidth=2,
            color=COLORS['mgn_light'], markersize=8, label='P99 Response')
    format_axis_labels(ax2,
                      xlabel=r'Pareto Shape Parameter ($\alpha$)',
                      ylabel='P99 Latency (sec)',
                      title='(B) P99 Latency vs $\\alpha$')
    ax2.legend()
    add_grid(ax2)

    # Subplot C: CV² vs α
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(df['alpha'], df['cv_squared'], marker='D', linewidth=2,
            color=COLORS['dedicated'], markersize=8)
    ax3.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5,
               label='Exponential (CV²=1)')
    format_axis_labels(ax3,
                      xlabel=r'Pareto Shape Parameter ($\alpha$)',
                      ylabel=r'Coefficient of Variation ($CV^2$)',
                      title='(C) Service Time Variability vs $\\alpha$')
    ax3.legend()
    add_grid(ax3)

    # Subplot D: Response time CDF
    ax4 = fig.add_subplot(gs[1, 1])

    # Plot CDFs for select α values
    plot_alphas = [2.1, 2.5, 3.0, 4.0]
    colors_map = {2.1: COLORS['mgn_heavy'], 2.5: COLORS['mgn_medium'],
                  3.0: COLORS['mgn_light'], 4.0: COLORS['dedicated']}

    for alpha in plot_alphas:
        response_times = all_response_times[alpha]
        sorted_data = np.sort(response_times)
        cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)

        ax4.plot(sorted_data, cdf, linewidth=2,
                label=f'α={alpha}', color=colors_map[alpha])

    format_axis_labels(ax4,
                      xlabel='Response Time (sec)',
                      ylabel='Cumulative Probability',
                      title='(D) Response Time CDF')
    ax4.legend()
    ax4.set_xlim(0, 0.5)
    add_grid(ax4)

    fig.suptitle('Heavy-Tail Impact on Queue Performance\n' +
                 r'M/G/N Queue: $\lambda=100$ msg/sec, $N=10$ threads, $\mu=12$ msg/sec/thread',
                 fontsize=14, fontweight='bold')

    save_figure(fig, 'visualization/plot_2_heavy_tail_impact')
    plt.close()

    return df


def plot_3_threading_comparison():
    """
    Plot 3: Threading Model Comparison (4 subplots)

    - Subplot A: Mean response time vs load
    - Subplot B: Throughput vs load
    - Subplot C: Rejection rate (dedicated)
    - Subplot D: Overhead factor (shared)
    """
    print("\n" + "="*70)
    print("Generating Plot 3: Threading Comparison")
    print("="*70)

    # Run threading comparison experiment
    NUM_THREADS = 20
    SERVICE_RATE = 12
    load_configs = [
        {'rho': 0.5, 'lambda': 120},
        {'rho': 0.6, 'lambda': 144},
        {'rho': 0.7, 'lambda': 168},
        {'rho': 0.8, 'lambda': 192},
        {'rho': 0.9, 'lambda': 216},
    ]

    results = []
    for config_dict in load_configs:
        arrival_rate = config_dict['lambda']
        rho = config_dict['rho']
        print(f"  Testing ρ={rho:.1f} (λ={arrival_rate})...")

        config = MMNConfig(
            arrival_rate=arrival_rate,
            num_threads=NUM_THREADS,
            service_rate=SERVICE_RATE,
            sim_duration=1000,
            warmup_time=100,
            random_seed=42
        )

        # Run all three models
        baseline_metrics = run_mmn_simulation(config)
        baseline_stats = baseline_metrics.summary_statistics()

        dedicated_metrics = run_dedicated_simulation(config, threads_per_connection=2)
        dedicated_stats = dedicated_metrics.summary_statistics()

        shared_metrics = run_shared_simulation(config, overhead_coefficient=0.1)
        shared_stats = shared_metrics.summary_statistics()

        results.append({
            'rho': rho,
            'arrival_rate': arrival_rate,
            'baseline_mean_response': baseline_stats['mean_response'],
            'baseline_throughput': baseline_stats['throughput'],
            'dedicated_mean_response': dedicated_stats['mean_response'],
            'dedicated_throughput': dedicated_stats['throughput'],
            'shared_mean_response': shared_stats['mean_response'],
            'shared_throughput': shared_stats['throughput'],
        })

    df = pd.DataFrame(results)

    # Create 2x2 subplot
    fig = plt.figure(figsize=(12, 10))
    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    # Subplot A: Mean response time vs load
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(df['rho'], df['baseline_mean_response'], marker='o',
            linewidth=2, label='M/M/N Baseline', color=COLORS['baseline'])
    ax1.plot(df['rho'], df['dedicated_mean_response'], marker='s',
            linewidth=2, label='Dedicated Threading', color=COLORS['dedicated'])
    ax1.plot(df['rho'], df['shared_mean_response'], marker='^',
            linewidth=2, label='Shared Threading', color=COLORS['shared'])
    format_axis_labels(ax1,
                      xlabel=r'System Load ($\rho$)',
                      ylabel='Mean Response Time (sec)',
                      title='(A) Response Time vs Load')
    ax1.legend()
    add_grid(ax1)

    # Subplot B: Throughput vs load
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(df['rho'], df['baseline_throughput'], marker='o',
            linewidth=2, label='M/M/N Baseline', color=COLORS['baseline'])
    ax2.plot(df['rho'], df['dedicated_throughput'], marker='s',
            linewidth=2, label='Dedicated Threading', color=COLORS['dedicated'])
    ax2.plot(df['rho'], df['shared_throughput'], marker='^',
            linewidth=2, label='Shared Threading', color=COLORS['shared'])
    format_axis_labels(ax2,
                      xlabel=r'System Load ($\rho$)',
                      ylabel='Throughput (msg/sec)',
                      title='(B) Throughput vs Load')
    ax2.legend()
    add_grid(ax2)

    # Subplot C: Rejection rate
    ax3 = fig.add_subplot(gs[1, 0])
    rejection_rate = (1 - df['dedicated_throughput'] / df['arrival_rate']) * 100
    ax3.plot(df['rho'], rejection_rate, marker='D',
            linewidth=2, color=COLORS['dedicated'], markersize=8)
    ax3.fill_between(df['rho'], 0, rejection_rate,
                     alpha=0.3, color=COLORS['dedicated'])
    format_axis_labels(ax3,
                      xlabel=r'System Load ($\rho$)',
                      ylabel='Rejection Rate (%)',
                      title='(C) Dedicated Threading: Connection Rejections')
    add_grid(ax3)

    # Subplot D: Performance ratio
    ax4 = fig.add_subplot(gs[1, 1])
    dedicated_ratio = df['dedicated_mean_response'] / df['baseline_mean_response']
    shared_ratio = df['shared_mean_response'] / df['baseline_mean_response']

    ax4.plot(df['rho'], dedicated_ratio, marker='s',
            linewidth=2, label='Dedicated/Baseline', color=COLORS['dedicated'])
    ax4.plot(df['rho'], shared_ratio, marker='^',
            linewidth=2, label='Shared/Baseline', color=COLORS['shared'])
    ax4.axhline(y=1.0, color='black', linestyle='--', linewidth=1,
               label='Baseline', alpha=0.5)
    format_axis_labels(ax4,
                      xlabel=r'System Load ($\rho$)',
                      ylabel='Response Time Ratio',
                      title='(D) Relative Performance')
    ax4.legend()
    add_grid(ax4)

    fig.suptitle('Threading Model Comparison: Dedicated vs Shared\n' +
                 r'$N=20$ threads, $\mu=12$ msg/sec/thread',
                 fontsize=14, fontweight='bold')

    save_figure(fig, 'visualization/plot_3_threading_comparison')
    plt.close()

    return df


def plot_4_load_testing():
    """
    Plot 4: Load Testing - All Models on Same Plot

    Shows how all 4 models (M/M/N, M/G/N with different α, Threading)
    perform across different load levels
    """
    print("\n" + "="*70)
    print("Generating Plot 4: Load Testing Comparison")
    print("="*70)

    # Test different load levels
    rhos = np.linspace(0.3, 0.9, 7)
    NUM_THREADS = 10
    SERVICE_RATE = 12

    results = []

    for rho in rhos:
        arrival_rate = rho * NUM_THREADS * SERVICE_RATE
        print(f"  Testing ρ={rho:.2f} (λ={arrival_rate:.1f})...")

        # M/M/N baseline
        mmn_config = MMNConfig(
            arrival_rate=arrival_rate,
            num_threads=NUM_THREADS,
            service_rate=SERVICE_RATE,
            sim_duration=1000,
            warmup_time=100,
            random_seed=42
        )
        mmn_metrics = run_mmn_simulation(mmn_config)
        mmn_stats = mmn_metrics.summary_statistics()

        # M/G/N with α=2.5 (moderate heavy tail)
        mgn_config = MGNConfig(
            arrival_rate=arrival_rate,
            num_threads=NUM_THREADS,
            service_rate=SERVICE_RATE,
            distribution="pareto",
            alpha=2.5,
            sim_duration=1000,
            warmup_time=100,
            random_seed=42
        )
        mgn_metrics = run_mgn_simulation(mgn_config)
        mgn_stats = mgn_metrics.summary_statistics()

        results.append({
            'rho': rho,
            'mmn_response': mmn_stats['mean_response'],
            'mgn_response': mgn_stats['mean_response'],
            'mmn_p95': mmn_stats['p95_response'],
            'mgn_p95': mgn_stats['p95_response'],
        })

    df = pd.DataFrame(results)

    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Mean response time
    ax1.plot(df['rho'], df['mmn_response'], marker='o', linewidth=2,
            label='M/M/N (Exponential)', color=COLORS['baseline'], markersize=8)
    ax1.plot(df['rho'], df['mgn_response'], marker='s', linewidth=2,
            label='M/G/N (Pareto α=2.5)', color=COLORS['mgn_medium'], markersize=8)
    format_axis_labels(ax1,
                      xlabel=r'System Load ($\rho$)',
                      ylabel='Mean Response Time (sec)',
                      title='Mean Response Time vs Load')
    ax1.legend()
    add_grid(ax1)

    # Plot 2: P95 response time
    ax2.plot(df['rho'], df['mmn_p95'], marker='o', linewidth=2,
            label='M/M/N (Exponential)', color=COLORS['baseline'], markersize=8)
    ax2.plot(df['rho'], df['mgn_p95'], marker='s', linewidth=2,
            label='M/G/N (Pareto α=2.5)', color=COLORS['mgn_medium'], markersize=8)
    format_axis_labels(ax2,
                      xlabel=r'System Load ($\rho$)',
                      ylabel='P95 Response Time (sec)',
                      title='P95 Response Time vs Load')
    ax2.legend()
    add_grid(ax2)

    fig.suptitle('Load Testing: Performance Under Varying Load\n' +
                 r'$N=10$ threads, $\mu=12$ msg/sec/thread',
                 fontsize=14, fontweight='bold')

    save_figure(fig, 'visualization/plot_4_load_testing')
    plt.close()

    return df


def main():
    """Generate all plots"""

    print("\n" + "="*70)
    print(" GENERATING ALL PUBLICATION-QUALITY PLOTS")
    print("="*70)

    # Setup style
    setup_plot_style()

    # Generate plots
    plot_1_mmn_validation()
    plot_2_heavy_tail_impact()
    plot_3_threading_comparison()
    plot_4_load_testing()

    print("\n" + "="*70)
    print("✓ ALL PLOTS GENERATED SUCCESSFULLY")
    print("="*70)
    print("\nGenerated files:")
    print("  - visualization/plot_1_mmn_validation.png (and .pdf)")
    print("  - visualization/plot_2_heavy_tail_impact.png (and .pdf)")
    print("  - visualization/plot_3_threading_comparison.png (and .pdf)")
    print("  - visualization/plot_4_load_testing.png (and .pdf)")
    print("\nAll plots saved at 300 DPI in PNG and PDF formats.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
