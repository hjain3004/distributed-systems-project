"""
Warmup Validation Script (MSER-5)
=================================

Scientifically determines the optimal warmup period using the 
Marginal Standard Error Rule (MSER-5) algorithm.

This addresses the critique: "Warmup Period Selection — Where's the Validation?"

Algorithm:
1. Run a long simulation to collect time-series data (waiting times).
2. Apply MSER-5 to detect the truncation point where the standard error of the mean is minimized.
3. Plot the transient phase and the detected steady-state start.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import TandemQueueConfig
from src.models.tandem_queue import run_tandem_simulation, TandemQueueSystem
import simpy

def run_long_simulation(duration=5000):
    """Run a long simulation to capture transient behavior"""
    print(f"Running long simulation ({duration}s)...")
    
    config = TandemQueueConfig(
        arrival_rate=100,
        n1=10, mu1=12, # rho = 0.83
        n2=15, mu2=12,
        network_delay=0.01,
        failure_prob=0.1,
        sim_duration=duration,
        warmup_time=0, # Capture everything
        distribution='pareto',
        alpha=2.1
    )
    
    env = simpy.Environment()
    system = TandemQueueSystem(env, config)
    
    # We need to access the raw time-series data
    # The system stores metrics in system.metrics
    system.run()
    
    # Extract waiting times and their timestamps
    # Note: TandemQueueSystem stores wait times as a list, but doesn't explicitly store timestamps for each wait
    # However, stage1_arrivals stores timestamps. We can approximate.
    # For MSER, we just need the sequence of observations.
    
    data = np.array(system.metrics.stage1_wait_times)
    return data

def mser5(data, batch_size=5):
    """
    Marginal Standard Error Rule (MSER-5)
    
    detects the index d* that minimizes the standard error of the mean
    of the truncated sequence.
    """
    n = len(data)
    m = n // batch_size
    
    # Create batches
    batches = [np.mean(data[i*batch_size : (i+1)*batch_size]) for i in range(m)]
    batches = np.array(batches)
    
    min_score = float('inf')
    optimal_d = 0
    
    # Iterate through possible truncation points
    # We only check the first half to ensure we keep enough data
    for d in range(m // 2):
        truncated = batches[d:]
        k = len(truncated)
        if k < 2: continue
        
        # MSER statistic: SEM of the truncated series
        # Score = Var(truncated) / k
        score = np.var(truncated, ddof=1) / k
        
        if score < min_score:
            min_score = score
            optimal_d = d
            
    # Convert back to observation index
    cutoff_index = optimal_d * batch_size
    return cutoff_index

def plot_warmup_analysis(data, cutoff_index):
    """Plot the time series and the cutoff point"""
    plt.figure(figsize=(12, 6))
    
    # Plot moving average for clarity
    window = 100
    series = pd.Series(data)
    ma = series.rolling(window=window).mean()
    
    plt.plot(data, alpha=0.3, color='gray', label='Raw Wait Times')
    plt.plot(ma, color='blue', linewidth=2, label=f'Moving Avg (w={window})')
    
    plt.axvline(x=cutoff_index, color='red', linestyle='--', linewidth=2, label=f'Recommended Cutoff (idx={cutoff_index})')
    
    plt.title("Warmup Analysis: Stage 1 Waiting Times (Pareto α=2.1)")
    plt.xlabel("Message Index")
    plt.ylabel("Waiting Time (s)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    os.makedirs('results/plots', exist_ok=True)
    plt.savefig('results/plots/warmup_validation.png')
    print("Saved plot to results/plots/warmup_validation.png")

def main():
    # 1. Get Data
    data = run_long_simulation()
    
    if len(data) == 0:
        print("Error: No data collected.")
        return

    # 2. Apply MSER-5
    cutoff_index = mser5(data)
    
    # 3. Estimate time equivalent
    # Arrival rate is 100 msg/s. So index 1000 ≈ 10 seconds.
    estimated_warmup_time = cutoff_index / 100.0
    
    print("\n" + "="*50)
    print(" WARMUP VALIDATION RESULTS (MSER-5)")
    print("="*50)
    print(f"Total Observations: {len(data)}")
    print(f"Optimal Truncation Index: {cutoff_index}")
    print(f"Estimated Warmup Time: {estimated_warmup_time:.2f} seconds")
    print(f"Current Configured Warmup: 200 seconds")
    
    if estimated_warmup_time < 200:
        print("✅ Current warmup (200s) is SUFFICIENT.")
    else:
        print("⚠️ Current warmup (200s) might be INSUFFICIENT.")
        
    # 4. Plot
    plot_warmup_analysis(data, cutoff_index)

if __name__ == "__main__":
    main()
