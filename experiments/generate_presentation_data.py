"""
Generate Presentation Data
==========================

Runs specific simulations to generate the exact data needed for the
"Reality Gap" and "Tail Risk" charts.

Output:
- results/data/reality_gap.csv
- results/data/tail_risk.csv
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import TandemQueueConfig
from src.models.tandem_queue import run_tandem_simulation
from src.analysis.analytical import TandemQueueAnalytical, MGNAnalytical

def generate_reality_gap_data():
    print("Generating 'Reality Gap' data...")
    
    # 1. Configure System (Heavy-Tailed)
    # Using the same config as heavy_tail_tandem.py
    config = TandemQueueConfig(
        arrival_rate=8.0,
        n1=1, mu1=12,
        n2=1, mu2=12,
        network_delay=0.01,
        failure_prob=0.1,
        sim_duration=20000,  # Long duration for stability
        warmup_time=2000,
        random_seed=42
    )
    
    # Inject Pareto distribution
    config.distribution = "pareto"
    config.alpha = 2.1
    
    # 2. Run Simulation (Ground Truth)
    print("  Running Simulation (Pareto, alpha=2.1)...")
    sim_results = run_tandem_simulation(config)
    sim_wait = sim_results['mean_stage1_wait']
    
    # 3. Analytical Models
    # A. M/M/1 Baseline (Paper) - Assumes exponential (CV=1)
    mmn_analytical = TandemQueueAnalytical(
        lambda_arrival=config.arrival_rate,
        n1=config.n1, mu1=config.mu1,
        n2=config.n2, mu2=config.mu2,
        network_delay=config.network_delay,
        failure_prob=config.failure_prob,
        cs_squared_1=1.0, # Exponential assumption
        cs_squared_2=1.0
    )
    mmn_wait = mmn_analytical.stage1_waiting_time()
    
    # B. QNA Model (Upper Bound) - Uses actual Pareto CV
    cs_squared = 1.0 / (config.alpha * (config.alpha - 2))
    qna_analytical = TandemQueueAnalytical(
        lambda_arrival=config.arrival_rate,
        n1=config.n1, mu1=config.mu1,
        n2=config.n2, mu2=config.mu2,
        network_delay=config.network_delay,
        failure_prob=config.failure_prob,
        cs_squared_1=cs_squared,
        cs_squared_2=cs_squared
    )
    qna_wait = qna_analytical.stage1_waiting_time()
    
    # 4. Save to CSV
    data = {
        'model': ['M/M/1 Model', 'Our Simulation', 'QNA Model'],
        'description': ['Paper Baseline', 'Ground Truth', 'Upper Bound'],
        'mean_wait_time': [mmn_wait, sim_wait, qna_wait]
    }
    df = pd.DataFrame(data)
    os.makedirs('results/data', exist_ok=True)
    df.to_csv('results/data/reality_gap.csv', index=False)
    print(f"  Saved results/data/reality_gap.csv")
    print(df)

def generate_tail_risk_data():
    print("\nGenerating 'Tail Risk' data...")
    
    # 1. Configure System (Heavy-Tailed)
    # Using M/G/1 scenario for clear tail analysis (N=1 exposes the tail)
    arrival_rate = 8.0 # Reduced for N=1
    num_threads = 1
    mean_service = 0.1 # mu = 10
    
    # Pareto alpha = 2.1
    alpha = 2.1
    
    config = TandemQueueConfig(
        arrival_rate=8.0,
        n1=1, mu1=10, 
        n2=1, mu2=10,
        network_delay=0.01,
        failure_prob=0.0,
        sim_duration=50000, # Longer for tail convergence
        warmup_time=2000,
        random_seed=123
    )
    config.distribution = "pareto"
    config.alpha = 2.1
    
    # 2. Run Simulation
    print("  Running Simulation (Pareto, alpha=2.1, N=1)...")
    sim_results = run_tandem_simulation(config)
    sim_p99 = sim_results.get('p99_end_to_end', 0.0)
    
    # 3. Analytical Models
    # A. Normal Approximation (Paper)
    # P99_Total ≈ Mean_Total + 2.33 * Sigma_Total
    # Mean_Total = 2 * (Wq + E[S]) + Network
    # Sigma_Total = sqrt(2 * Var(R))
    
    # Calculate single stage metrics
    cv_squared = 1.0 / (alpha * (alpha - 2))
    variance_service = cv_squared * (mean_service ** 2)
    
    mgn = MGNAnalytical(arrival_rate, num_threads, mean_service, variance_service)
    mean_R = mgn.mean_response_time()
    
    # Var(R) ≈ Var(W) + Var(S)
    # For M/G/1: Var(W) ≈ (E[W])^2 * (something)? 
    # Let's use the MGNAnalytical.p99_response_time() logic which approximates Sigma
    # Sigma_R ≈ sqrt(VarS * (1 + C^2)) -> This is a rough heuristic in the code
    # Let's stick to the method in the code to be consistent with "Paper's Model"
    normal_p99_stage = mgn.p99_response_time()
    sigma_stage = (normal_p99_stage - mean_R) / 2.33
    
    mean_total = 2 * mean_R + config.network_delay * 2
    sigma_total = np.sqrt(2 * (sigma_stage**2))
    normal_p99_total = mean_total + 2.33 * sigma_total
    
    # B. EVT/Heavy-Tail Approximation (Ours)
    # Now valid because N=1
    evt_p99_stage = mgn.p99_response_time_heavy_tail()
    
    # Dominance Principle for Tandem Heavy Tail
    # P99_Total ≈ P99_Stage1 + Mean_Stage2 + Network
    evt_p99_total = evt_p99_stage + mean_R + config.network_delay * 2
    
    data = {
        'method': ['Normal Approx', 'EVT Estimate', 'Empirical Truth'],
        'description': ['Paper (Normal)', 'Ours (Heavy-Tail)', 'Simulation'],
        'p99_value': [normal_p99_total, evt_p99_total, sim_p99]
    }
    
    df = pd.DataFrame(data)
    df.to_csv('results/data/tail_risk.csv', index=False)
    print(f"  Saved results/data/tail_risk.csv")
    print(df)

if __name__ == "__main__":
    generate_reality_gap_data()
    generate_tail_risk_data()
