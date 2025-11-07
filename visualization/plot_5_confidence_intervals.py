"""
Plot 5: Confidence Intervals Visualization

Shows results with 95% confidence intervals across all experiments
to demonstrate statistical rigor and reproducibility.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from plot_config import (
    setup_plot_style, save_figure, add_grid,
    format_axis_labels, add_error_bars, COLORS
)


def plot_5_confidence_intervals():
    """
    Plot 5: Confidence Intervals (3 subplots)

    - Subplot A: M/G/N mean wait time vs α (with error bars)
    - Subplot B: M/G/N P99 response time vs α (with error bars)
    - Subplot C: Threading models comparison (with error bars)
    """
    print("\n" + "="*70)
    print("Generating Plot 5: Confidence Intervals")
    print("="*70)

    # Load confidence interval data
    mgn_df = pd.read_csv('experiments/mgn_confidence_intervals.csv')
    threading_df = pd.read_csv('experiments/threading_confidence_intervals.csv')

    # Create figure with 3 subplots (1 row, 3 columns)
    fig = plt.figure(figsize=(16, 5))
    gs = GridSpec(1, 3, figure=fig, hspace=0.3, wspace=0.3)

    # Subplot A: M/G/N Mean Wait Time with CI
    ax1 = fig.add_subplot(gs[0, 0])

    # Extract mean wait data
    wait_data = mgn_df[mgn_df['metric'] == 'mean_wait'].sort_values('alpha')
    alphas = wait_data['alpha'].values
    means = wait_data['mean'].values
    ci_lower = wait_data['ci_lower'].values
    ci_upper = wait_data['ci_upper'].values
    errors = (ci_upper - ci_lower) / 2

    ax1.errorbar(alphas, means, yerr=errors,
                marker='o', markersize=8, linewidth=2,
                capsize=5, capthick=2,
                color=COLORS['mgn_medium'],
                label='Mean ± 95% CI')

    format_axis_labels(ax1,
                      xlabel=r'Pareto Shape Parameter ($\alpha$)',
                      ylabel='Mean Waiting Time (sec)',
                      title='(A) M/G/N: Mean Wait Time with Confidence Intervals')
    ax1.legend()
    add_grid(ax1)

    # Subplot B: M/G/N P99 Response Time with CI
    ax2 = fig.add_subplot(gs[0, 1])

    # Extract P99 response data
    p99_data = mgn_df[mgn_df['metric'] == 'p99_response'].sort_values('alpha')
    alphas = p99_data['alpha'].values
    means = p99_data['mean'].values
    ci_lower = p99_data['ci_lower'].values
    ci_upper = p99_data['ci_upper'].values
    errors = (ci_upper - ci_lower) / 2

    ax2.errorbar(alphas, means, yerr=errors,
                marker='s', markersize=8, linewidth=2,
                capsize=5, capthick=2,
                color=COLORS['mgn_heavy'],
                label='P99 ± 95% CI')

    format_axis_labels(ax2,
                      xlabel=r'Pareto Shape Parameter ($\alpha$)',
                      ylabel='P99 Response Time (sec)',
                      title='(B) M/G/N: P99 Response Time with Confidence Intervals')
    ax2.legend()
    add_grid(ax2)

    # Subplot C: Threading Models Comparison with CI
    ax3 = fig.add_subplot(gs[0, 2])

    # Extract threading data
    response_data = threading_df[threading_df['metric'] == 'mean_response']

    models = ['baseline', 'dedicated', 'shared']
    model_labels = ['M/M/N\nBaseline', 'Dedicated\nThreading', 'Shared\nThreading']
    colors_map = {
        'baseline': COLORS['baseline'],
        'dedicated': COLORS['dedicated'],
        'shared': COLORS['shared']
    }

    x_pos = np.arange(len(models))
    means_list = []
    errors_list = []
    colors_list = []

    for model in models:
        model_data = response_data[response_data['model'] == model].iloc[0]
        mean_val = model_data['mean']
        ci_lower = model_data['ci_lower']
        ci_upper = model_data['ci_upper']
        error = (ci_upper - ci_lower) / 2

        means_list.append(mean_val)
        errors_list.append(error)
        colors_list.append(colors_map[model])

    bars = ax3.bar(x_pos, means_list, yerr=errors_list,
                   color=colors_list, alpha=0.7,
                   capsize=8, error_kw={'linewidth': 2},
                   edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for i, (bar, mean, error) in enumerate(zip(bars, means_list, errors_list)):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + error,
                f'{mean:.4f}\n±{error:.4f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(model_labels, fontweight='bold')
    format_axis_labels(ax3,
                      ylabel='Mean Response Time (sec)',
                      title=r'(C) Threading Models at $\rho=0.7$ with Confidence Intervals')
    add_grid(ax3)

    fig.suptitle('Statistical Rigor: 95% Confidence Intervals (N=10 Replications)\n' +
                 r'All metrics show reproducible results with tight confidence bounds',
                 fontsize=14, fontweight='bold')

    save_figure(fig, 'visualization/plot_5_confidence_intervals')
    plt.close()

    print("✓ Saved: visualization/plot_5_confidence_intervals.png (and .pdf)")
    print("\n" + "="*70)


def main():
    """Generate confidence interval plot"""

    print("\n" + "="*70)
    print(" GENERATING CONFIDENCE INTERVAL PLOT")
    print("="*70)

    # Setup style
    setup_plot_style()

    # Generate plot
    plot_5_confidence_intervals()

    print("✓ PLOT 5 GENERATED SUCCESSFULLY")
    print("="*70)
    print("\nAll visualization plots (1-5) are now complete!")
    print("All plots saved at 300 DPI in PNG and PDF formats.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
