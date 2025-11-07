"""
Visualization configuration and utilities

Provides consistent styling for all plots
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

# Color palette
COLORS = {
    'baseline': '#2C3E50',      # Dark blue-gray
    'analytical': '#E74C3C',    # Red
    'simulation': '#3498DB',    # Blue
    'dedicated': '#27AE60',     # Green
    'shared': '#F39C12',        # Orange
    'mmn': '#9B59B6',           # Purple
    'mgn_light': '#1ABC9C',     # Turquoise (α=3.0)
    'mgn_medium': '#E67E22',    # Dark orange (α=2.5)
    'mgn_heavy': '#C0392B',     # Dark red (α=2.1)
}

# Line styles
LINESTYLES = {
    'analytical': '--',
    'simulation': '-',
    'baseline': '-',
    'dedicated': '-',
    'shared': '-.',
}

# Markers
MARKERS = {
    'analytical': 'o',
    'simulation': 's',
    'baseline': '^',
    'dedicated': 'D',
    'shared': 'v',
}


def setup_plot_style():
    """Apply seaborn style with custom tweaks"""
    sns.set_style("whitegrid", {
        'grid.linestyle': '--',
        'grid.alpha': 0.3,
        'axes.edgecolor': '.2',
        'axes.linewidth': 1.0,
    })
    sns.set_palette("husl")


def save_figure(fig, filename, tight_layout=True):
    """
    Save figure with consistent settings

    Args:
        fig: matplotlib figure
        filename: output filename (without extension)
        tight_layout: apply tight_layout before saving
    """
    if tight_layout:
        fig.tight_layout()

    # Save as PNG and PDF
    fig.savefig(f'{filename}.png', dpi=300, bbox_inches='tight')
    fig.savefig(f'{filename}.pdf', bbox_inches='tight')
    print(f"✓ Saved: {filename}.png and {filename}.pdf")


def add_grid(ax, alpha=0.3):
    """Add subtle grid to axis"""
    ax.grid(True, linestyle='--', alpha=alpha, linewidth=0.5)
    ax.set_axisbelow(True)


def format_axis_labels(ax, xlabel=None, ylabel=None, title=None):
    """Apply consistent label formatting"""
    if xlabel:
        ax.set_xlabel(xlabel, fontweight='bold')
    if ylabel:
        ax.set_ylabel(ylabel, fontweight='bold')
    if title:
        ax.set_title(title, fontweight='bold', pad=10)


def add_error_bars(ax, x, y, yerr, label=None, color=None, alpha=0.2):
    """Add error bars with shaded region"""
    if color is None:
        color = COLORS['simulation']

    # Plot line
    line = ax.plot(x, y, marker='o', label=label, color=color, linewidth=2)[0]

    # Add shaded region for error
    ax.fill_between(x,
                     np.array(y) - np.array(yerr),
                     np.array(y) + np.array(yerr),
                     alpha=alpha, color=color)

    return line


def add_statistical_annotation(ax, x1, x2, y, pvalue, text_offset=0.05):
    """
    Add statistical significance annotation

    Args:
        ax: matplotlib axis
        x1, x2: x-positions to connect
        y: y-position of annotation
        pvalue: p-value
        text_offset: vertical offset for text
    """
    # Determine significance stars
    if pvalue < 0.001:
        stars = '***'
    elif pvalue < 0.01:
        stars = '**'
    elif pvalue < 0.05:
        stars = '*'
    else:
        stars = 'n.s.'

    # Draw connecting line
    ax.plot([x1, x1, x2, x2], [y, y+text_offset, y+text_offset, y],
            'k-', linewidth=1)

    # Add text
    ax.text((x1+x2)/2, y+text_offset, stars,
            ha='center', va='bottom', fontsize=10, fontweight='bold')
