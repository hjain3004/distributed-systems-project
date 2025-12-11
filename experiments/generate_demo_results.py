
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import HeterogeneousMMNConfig, ServerGroup
from src.models.heterogeneous_mmn import run_heterogeneous_mmn_simulation

def run_phase(phase_name, config, duration=20):
    """Run a simulation phase and return the metrics dataframe"""
    print(f"Running Phase: {phase_name}...")
    
    # Update config duration
    config.sim_duration = duration
    config.warmup_time = 0 # No warmup for sequential phases
    
    metrics = run_heterogeneous_mmn_simulation(config)
    df = metrics.to_dataframe()
    
    # Add phase label
    df['phase'] = phase_name
    
    # Calculate rolling P99 for visualization
    df['p99_latency'] = df['response_time'].rolling(window=50).quantile(0.99)
    df['mean_latency'] = df['response_time'].rolling(window=50).mean()
    
    return df

def main():
    print("Generating Demo Results...")
    
    # Common Config
    ARRIVAL_RATE = 50
    DURATION_PER_PHASE = 30 # seconds
    
    all_data = []
    current_time_offset = 0
    
    # --- Phase 1: Baseline (Homogeneous, Weak, No Stealing) ---
    config_1 = HeterogeneousMMNConfig(
        arrival_rate=ARRIVAL_RATE,
        server_groups=[ServerGroup(count=5, service_rate=12.0)], # Homogeneous
        selection_policy="random",
        work_stealing=False,
        consistency_mode="eventual",
        enable_qos=False,
        sim_duration=DURATION_PER_PHASE
    )
    df_1 = run_phase("1. Baseline", config_1)
    df_1['time_offset'] = df_1['arrival_time'] + current_time_offset
    all_data.append(df_1)
    current_time_offset += DURATION_PER_PHASE
    
    # --- Phase 2: The Crash (Heterogeneous, No Stealing) ---
    # 40% Legacy = 2 Slow (rate 3.0), 3 Fast (rate 15.0) -> Avg 10.2 < 12
    # Capacity drops from 60 to 51. Arrival 50. Utilization ~98%.
    # With variance, this crashes.
    config_2 = HeterogeneousMMNConfig(
        arrival_rate=ARRIVAL_RATE,
        server_groups=[
            ServerGroup(count=2, service_rate=3.0, name="Legacy"), # 1/4th speed
            ServerGroup(count=3, service_rate=15.0, name="Fast")
        ],
        selection_policy="random",
        work_stealing=False,
        consistency_mode="eventual",
        enable_qos=False,
        sim_duration=DURATION_PER_PHASE
    )
    df_2 = run_phase("2. The Crash", config_2)
    df_2['time_offset'] = df_2['arrival_time'] + current_time_offset
    all_data.append(df_2)
    current_time_offset += DURATION_PER_PHASE
    
    # --- Phase 3: The Fix (Work Stealing) ---
    config_3 = HeterogeneousMMNConfig(
        arrival_rate=ARRIVAL_RATE,
        server_groups=[
            ServerGroup(count=2, service_rate=3.0, name="Legacy"),
            ServerGroup(count=3, service_rate=15.0, name="Fast")
        ],
        selection_policy="random",
        work_stealing=True, # ENABLED
        consistency_mode="eventual",
        enable_qos=False,
        sim_duration=DURATION_PER_PHASE
    )
    df_3 = run_phase("3. The Fix", config_3)
    df_3['time_offset'] = df_3['arrival_time'] + current_time_offset
    all_data.append(df_3)
    current_time_offset += DURATION_PER_PHASE
    
    # --- Phase 4: Safety Tax (2PC) ---
    config_4 = HeterogeneousMMNConfig(
        arrival_rate=ARRIVAL_RATE,
        server_groups=[
            ServerGroup(count=2, service_rate=3.0, name="Legacy"),
            ServerGroup(count=3, service_rate=15.0, name="Fast")
        ],
        selection_policy="random",
        work_stealing=True,
        consistency_mode="strong_2pc", # ENABLED
        enable_qos=False,
        sim_duration=DURATION_PER_PHASE
    )
    df_4 = run_phase("4. Safety Tax", config_4)
    df_4['time_offset'] = df_4['arrival_time'] + current_time_offset
    all_data.append(df_4)
    current_time_offset += DURATION_PER_PHASE

    # --- Phase 5: QoS (Zero Sum) ---
    # Note: QoS logic is complex to simulate in one go without specific VIP tagging
    # For this script, we'll simulate the "Standard" user experience getting worse
    # We simulate this by reducing effective capacity for standard users
    config_5 = HeterogeneousMMNConfig(
        arrival_rate=ARRIVAL_RATE,
        server_groups=[
            ServerGroup(count=2, service_rate=3.0, name="Legacy"),
            ServerGroup(count=3, service_rate=15.0, name="Fast")
        ],
        selection_policy="random",
        work_stealing=True,
        consistency_mode="strong_2pc",
        enable_qos=True, # ENABLED
        sim_duration=DURATION_PER_PHASE
    )
    df_5 = run_phase("5. QoS Impact", config_5)
    df_5['time_offset'] = df_5['arrival_time'] + current_time_offset
    all_data.append(df_5)
    
    # --- Combine & Save ---
    full_df = pd.concat(all_data)
    
    # Save Data
    os.makedirs("results/data", exist_ok=True)
    csv_path = "results/data/demo_metrics.csv"
    full_df.to_csv(csv_path, index=False)
    print(f"Data saved to {csv_path}")
    
    # --- Plotting ---
    print("Generating Plot...")
    plt.figure(figsize=(15, 8))
    
    # Plot Mean Latency
    plt.plot(full_df['time_offset'], full_df['mean_latency'], label='Mean Latency', color='blue', alpha=0.6)
    
    # Plot P99 Latency
    plt.plot(full_df['time_offset'], full_df['p99_latency'], label='P99 Latency', color='red', linestyle='--', alpha=0.8)
    
    # Add Phase Dividers
    phases = full_df['phase'].unique()
    phase_starts = [0, 30, 60, 90, 120]
    
    for i, phase in enumerate(phases):
        plt.axvline(x=phase_starts[i], color='gray', linestyle=':', alpha=0.5)
        plt.text(phase_starts[i] + 1, plt.ylim()[1]*0.95, phase, rotation=0, fontweight='bold')
        
    plt.title("Distributed Systems Demo: The Narrative Arc", fontsize=16)
    plt.xlabel("Simulation Time (s)", fontsize=12)
    plt.ylabel("Latency (s)", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save Plot
    os.makedirs("results/plots", exist_ok=True)
    plot_path = "results/plots/demo_narrative.png"
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")

if __name__ == "__main__":
    main()
