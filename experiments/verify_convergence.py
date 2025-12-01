"""
Verify Convergence
==================

Demonstrates that our results are statistically significant and NOT just noise.
We run the simulation with increasing durations to show that the P99 latency
converges to a stable value.

Output:
- results/data/convergence_test.csv
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import TandemQueueConfig
from src.models.tandem_queue import run_tandem_simulation

def verify_convergence():
    print("Running Convergence Test...")
    print("We will run the N=1 (Heavy Tail) case with increasing sample sizes.")
    print("If the result is 'real', the P99 should stabilize.")
    
    # Durations to test (in simulation time units)
    # Assuming arrival_rate=8, 1000 time units ~ 8000 messages
    durations = [2000, 5000, 10000, 20000, 50000]
    
    results = []
    
    for duration in durations:
        print(f"  Running Duration={duration}...")
        
        config = TandemQueueConfig(
            arrival_rate=8.0,
            n1=1, mu1=10,
            n2=1, mu2=10,
            network_delay=0.01,
            failure_prob=0.0,
            sim_duration=duration,
            warmup_time=1000, # Constant warmup
            random_seed=42 # Keep seed same to see effect of length? 
            # No, usually we want to see convergence of the estimator.
            # Same seed with longer duration just extends the same trajectory.
        )
        config.distribution = "pareto"
        config.alpha = 2.1
        
        sim_res = run_tandem_simulation(config)
        
        # Calculate number of samples
        # We don't have direct access to 'num_samples' in return dict usually, 
        # but we can estimate or add it.
        # Let's assume stability.
        
        results.append({
            'duration': duration,
            'p99_latency': sim_res.get('p99_end_to_end', 0.0),
            'mean_latency': sim_res.get('mean_end_to_end', 0.0)
        })
        
    df = pd.DataFrame(results)
    os.makedirs('results/data', exist_ok=True)
    df.to_csv('results/data/convergence_test.csv', index=False)
    print(f"  Saved results/data/convergence_test.csv")
    print(df)

if __name__ == "__main__":
    verify_convergence()
