"""
Check Convergence Script
========================

Empirically determines the number of replications needed for stable estimates
under heavy-tailed conditions (Pareto alpha=2.1).

Addresses the critique: "20 replications is bare minimum... Did you verify?"

Method:
1. Run simulations with increasing N (10, 20, 50, 100, 200).
2. Calculate Mean and 95% CI for each N.
3. Plot CI Width vs N to show convergence.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import TandemQueueConfig
from src.models.tandem_queue import run_tandem_simulation

def run_convergence_study():
    print("Running Convergence Study (Heavy-Tail Pareto alpha=2.1)...")
    
    # Heavy-tailed configuration
    config = TandemQueueConfig(
        arrival_rate=100,
        n1=10, mu1=12,
        n2=15, mu2=12,
        network_delay=0.01,
        failure_prob=0.1,
        sim_duration=1000, # Shorter duration for speed, but enough for steady state
        warmup_time=200,
        distribution='pareto',
        alpha=2.1
    )
    
    # Replication counts to test
    n_replications = [10, 20, 50, 100, 200]
    results = []
    
    # We collect a large pool of samples first, then subsample
    max_n = max(n_replications)
    print(f"Collecting {max_n} samples...")
    
    samples = []
    for _ in tqdm(range(max_n)):
        stats = run_tandem_simulation(config)
        samples.append(stats['mean_end_to_end'])
        
    samples = np.array(samples)
    
    print("\nAnalyzing convergence...")
    for n in n_replications:
        # Take first n samples
        subset = samples[:n]
        
        mean = np.mean(subset)
        std_err = np.std(subset, ddof=1) / np.sqrt(n)
        ci_width = 1.96 * std_err
        
        # Relative CI width (as % of mean)
        rel_ci_width = (ci_width / mean) * 100
        
        results.append({
            'N': n,
            'Mean': mean,
            'CI_Width_Abs': ci_width,
            'CI_Width_Pct': rel_ci_width
        })
        
        print(f"  N={n:3d}: Mean={mean:.4f} ± {ci_width:.4f} ({rel_ci_width:.1f}%)")
        
    # Plot
    df = pd.DataFrame(results)
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['N'], df['CI_Width_Pct'], 'o-', linewidth=2, color='purple')
    plt.axhline(y=5.0, color='green', linestyle='--', label='Target (5% Error)')
    plt.axhline(y=1.0, color='blue', linestyle='--', label='Target (1% Error)')
    
    plt.xlabel('Number of Replications')
    plt.ylabel('95% CI Width (% of Mean)')
    plt.title('Statistical Convergence: Heavy-Tailed Workload (Pareto α=2.1)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    os.makedirs('results/plots', exist_ok=True)
    plt.savefig('results/plots/convergence_check.png')
    print("\nSaved plot to results/plots/convergence_check.png")
    
    # Recommendation
    best_n = df[df['CI_Width_Pct'] < 5.0]['N'].min()
    if pd.isna(best_n):
        print("\n⚠️ Even 200 replications didn't reach 5% stability!")
    else:
        print(f"\n✅ {best_n} replications needed for <5% margin of error.")

if __name__ == "__main__":
    run_convergence_study()
