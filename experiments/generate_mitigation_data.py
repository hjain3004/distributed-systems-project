"""
Generate Mitigation Data
========================

Demonstrates how to "tame the tail".
Problem: Heavy-tailed workloads cause massive P99 latency with N=1 (7.8s).
Solution: Our simulation proves that adding just 1-2 servers drastically reduces this risk.

Output:
- results/data/mitigation_scaling.csv
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import TandemQueueConfig
from src.models.tandem_queue import run_tandem_simulation

def generate_scaling_data():
    print("Generating 'Mitigation Scaling' data...")
    
    # Common Config (Heavy-Tailed)
    arrival_rate = 8.0
    mu = 10.0 # Capacity per server = 10
    
    # We want to show P99 vs N (1, 2, 3)
    results = []
    
    for n in [1, 2, 3, 4]:
        print(f"  Running Simulation (N={n})...")
        
        config = TandemQueueConfig(
            arrival_rate=arrival_rate,
            n1=n, mu1=mu,
            n2=n, mu2=mu,
            network_delay=0.01,
            failure_prob=0.0,
            sim_duration=20000,
            warmup_time=2000,
            random_seed=42
        )
        config.distribution = "pareto"
        config.alpha = 2.1
        
        sim_res = run_tandem_simulation(config)
        p99 = sim_res.get('p99_end_to_end', 0.0)
        mean = sim_res.get('mean_end_to_end', 0.0)
        
        results.append({
            'servers': n,
            'capacity': n * mu,
            'utilization': arrival_rate / (n * mu),
            'p99_latency': p99,
            'mean_latency': mean
        })
        
    df = pd.DataFrame(results)
    os.makedirs('results/data', exist_ok=True)
    df.to_csv('results/data/mitigation_scaling.csv', index=False)
    print(f"  Saved results/data/mitigation_scaling.csv")
    print(df)

if __name__ == "__main__":
    generate_scaling_data()
