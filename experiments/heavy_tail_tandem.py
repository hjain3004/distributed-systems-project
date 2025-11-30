"""
Experiment: Tandem Queue with Heavy-Tailed Service Times
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import TandemQueueConfig
from src.models.tandem_queue import run_tandem_simulation
from src.analysis.analytical import TandemQueueAnalytical

# Create a custom config class that allows distribution parameters
# Since TandemQueueConfig doesn't explicitly have 'distribution' field in the original file,
# but our modified code looks for getattr(config, 'distribution'), we can monkey-patch or subclass.
# However, Pydantic models are strict. Let's try to just pass it if the model allows extra fields,
# or we might need to modify the config class too. 
# Checking src/core/config.py, TandemQueueConfig inherits from BaseModel, not QueueConfig.
# It does NOT have 'distribution' field. 
# But our code uses `getattr(config, 'distribution', 'exponential')`.
# So we can just add the attribute to the instance if Pydantic allows it, or use a dynamic approach.

def run_heavy_tail_experiment():
    print("="*70)
    print("EXPERIMENT: Heavy-Tailed Tandem Queue (Pareto)")
    print("="*70)

    # 1. Configure System
    config = TandemQueueConfig(
        arrival_rate=8.0,      # Reduced for N=1 (Capacity = 12)
        n1=1, mu1=12,          # Single server to expose tail latency
        n2=1, mu2=12,
        network_delay=0.01,
        failure_prob=0.1,
        sim_duration=10000,    # Longer simulation
        warmup_time=1000,
        random_seed=42
    )
    
    # INJECT DISTRIBUTION PARAMETERS
    # This works because we used getattr() in the model code
    config.distribution = "pareto"
    config.alpha = 2.1  # Very heavy tail (infinite variance is alpha <= 2)
    
    print("\nConfiguration:")
    print(f"  Distribution: Pareto (α={config.alpha})")
    print(f"  λ = {config.arrival_rate}")
    print(f"  Stage 1 ρ = {config.stage1_utilization:.3f}")
    print(f"  Stage 2 ρ = {config.stage2_utilization:.3f}")

    # 2. Run Simulation
    print("\nRunning simulation (this may take a moment)...")
    sim_results = run_tandem_simulation(config)
    
    # Calculate CV squared for Pareto
    # C^2 = 1 / (alpha * (alpha - 2)) for alpha > 2
    if config.alpha > 2:
        cs_squared = 1.0 / (config.alpha * (config.alpha - 2))
    else:
        cs_squared = 100.0 # Infinite variance proxy
        
    print(f"  Service CV² = {cs_squared:.2f}")

    # 3. Analytical Model (Now using QNA Approximation)
    analytical = TandemQueueAnalytical(
        lambda_arrival=config.arrival_rate,
        n1=config.n1, mu1=config.mu1,
        n2=config.n2, mu2=config.mu2,
        network_delay=config.network_delay,
        failure_prob=config.failure_prob,
        cs_squared_1=cs_squared,
        cs_squared_2=cs_squared
    )
    
    # 4. Compare
    print(f"\n{'Metric':<30} {'Analytical (QNA)':>20} {'Simulation (Pareto)':>20} {'Difference':>15}")
    print("-" * 90)
    
    metrics = [
        ('Stage 1 Mean Wait', 'stage1_mean_wait', 'mean_stage1_wait'),
        ('Stage 2 Mean Wait', 'stage2_mean_wait', 'mean_stage2_wait'),
        ('Total End-to-End', 'total_delivery_time', 'mean_end_to_end')
    ]
    
    analytical_metrics = analytical.all_metrics()
    
    for label, a_key, s_key in metrics:
        val_a = analytical_metrics[a_key]
        val_s = sim_results[s_key]
        diff_pct = (val_s - val_a) / val_a * 100
        
        print(f"{label:<30} {val_a:>20.6f} {val_s:>20.6f} {diff_pct:>14.1f}%")
        
    print("\nAnalysis:")
    print("If Simulation >> Analytical, it confirms that heavy-tailed service times")
    print("cause massive performance degradation that the standard M/M/n model misses.")
    print("This validates the importance of your heavy-tail implementation.")

if __name__ == "__main__":
    run_heavy_tail_experiment()
