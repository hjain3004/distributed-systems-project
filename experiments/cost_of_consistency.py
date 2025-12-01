import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import simpy
import random
import numpy as np
import pandas as pd
from src.core.config import MMNConfig
from src.core.distributions import ParetoService
from src.models.cloud_message import CloudMessage
from src.models.distributed_broker import DistributedBroker

def run_ordering_experiment(ordering_mode: str, arrival_rate=80, service_rate=100, duration=500):
    env = simpy.Environment()
    
    # Setup Broker
    broker = DistributedBroker(env, num_nodes=1, replication_factor=1, ordering_mode=ordering_mode)
    
    # Metrics
    latencies = []
    
    # Service Process (Consumer)
    def consumer(env, broker):
        while True:
            msg = broker.receive_message()
            if msg:
                # Simulate processing time (Pareto - Heavy Tail)
                # Using Pareto to exacerbate HOL blocking effects
                # Alpha 1.5 = Infinite Variance = Massive Stragglers
                service_time = random.paretovariate(1.5) * (1.0/service_rate) 
                yield env.timeout(service_time)
                
                broker.acknowledge_message(msg)
                
                # Record latency
                latency = env.now - msg.arrival_time
                latencies.append(latency)
            else:
                # Wait if no message available (or blocked)
                yield env.timeout(0.001) # Poll interval

    # Arrival Process (Producer) with Network Jitter
    def producer(env, broker):
        msg_id = 0
        while True:
            interarrival = random.expovariate(arrival_rate)
            yield env.timeout(interarrival)
            
            # Create message
            msg = CloudMessage(
                id=msg_id,
                content=f"msg-{msg_id}",
                arrival_time=env.now
            )
            # Set sequence number for In-Order delivery
            msg.vector_clock = [msg_id]
            
            # Simulate Network Jitter (The "Slow Path" vs "Fast Path")
            # Some messages get delayed, causing out-of-order arrival
            delay = random.uniform(0.01, 0.1) # 10ms to 100ms jitter
            env.process(delayed_publish(env, broker, msg, delay))
            
            msg_id += 1

    def delayed_publish(env, broker, msg, delay):
        yield env.timeout(delay)
        broker.publish_message(msg)

    # Start processes
    env.process(producer(env, broker))
    # Multiple consumers to create out-of-order processing opportunities
    for _ in range(5): 
        env.process(consumer(env, broker))
        
    # Run simulation
    env.run(until=duration)
    
    return latencies

if __name__ == "__main__":
    print("Running 'Cost of Consistency' Experiment...")
    print("-" * 50)
    
    # 1. Out-of-Order (Baseline)
    print("Running Out-of-Order Simulation...")
    latencies_ooo = run_ordering_experiment("out_of_order")
    p99_ooo = np.percentile(latencies_ooo, 99)
    mean_ooo = np.mean(latencies_ooo)
    print(f"Out-of-Order P99: {p99_ooo*1000:.2f} ms")
    print(f"Out-of-Order Mean: {mean_ooo*1000:.2f} ms")
    
    # 2. In-Order (Experiment)
    print("\nRunning In-Order Simulation...")
    latencies_io = run_ordering_experiment("in_order")
    p99_io = np.percentile(latencies_io, 99)
    mean_io = np.mean(latencies_io)
    print(f"In-Order P99:     {p99_io*1000:.2f} ms")
    print(f"In-Order Mean:     {mean_io*1000:.2f} ms")
    
    # 3. Comparison
    cost_percent = ((mean_io - mean_ooo) / mean_ooo) * 100
    print("-" * 50)
    print(f"Cost of Consistency (Mean): +{cost_percent:.1f}% Latency")
    print("-" * 50)
    
    # Save results for graph
    results = pd.DataFrame({
        'Mode': ['Out-of-Order', 'In-Order'],
        'P99_Latency_ms': [p99_ooo*1000, p99_io*1000],
        'Mean_Latency_ms': [mean_ooo*1000, mean_io*1000]
    })
    results.to_csv('experiments/ordering_mode_results.csv', index=False)
    print("Results saved to experiments/ordering_mode_results.csv")
