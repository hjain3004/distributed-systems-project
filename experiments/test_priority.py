
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.priority_queue import run_priority_queue_simulation
from src.core.config import PriorityQueueConfig

def test_priority_queue():
    config = PriorityQueueConfig(
        arrival_rate=100,
        num_threads=10,
        service_rate=12,
        num_priorities=2,
        priority_rates=[20, 80], # 20% VIP
        preemptive=True,
        sim_duration=1000,
        warmup_time=100
    )
    
    results = run_priority_queue_simulation(config)
    
    print("\nResults:")
    for p, metrics in results.items():
        print(f"Priority {p}: Mean Wait = {metrics['mean_wait']:.4f}s")

    assert results[1]['mean_wait'] < results[2]['mean_wait'], "VIP should wait less"
    print("Test Passed!")

if __name__ == "__main__":
    test_priority_queue()
