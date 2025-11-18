"""
Tandem Queue Model - Li et al. (2015)

Two-stage queueing system modeling cloud message broker architecture:

Stage 1 (Broker):  Publishers → Broker Queue → Send to Network
Stage 2 (Receiver): Network → Receiver Queue → Consumers

Key Features:
- Two independent M/M/n queues in series
- Network layer with delay D_link and failure probability p
- Stage 2 sees HIGHER arrival rate: Λ₂ = λ/(1-p) due to retransmissions
- End-to-end latency includes both queueing delays and network time
"""

import simpy
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass, field

from .network_layer import NetworkLayer


@dataclass
class TandemMetrics:
    """Comprehensive metrics for tandem queue system"""

    # End-to-end latency
    end_to_end_times: List[float] = field(default_factory=list)

    # Stage-specific times
    stage1_wait_times: List[float] = field(default_factory=list)
    stage1_service_times: List[float] = field(default_factory=list)

    network_times: List[float] = field(default_factory=list)

    stage2_wait_times: List[float] = field(default_factory=list)
    stage2_service_times: List[float] = field(default_factory=list)

    # Arrival times at each stage
    stage1_arrivals: List[float] = field(default_factory=list)
    stage2_arrivals: List[float] = field(default_factory=list)

    # Queue lengths
    stage1_queue_lengths: List[int] = field(default_factory=list)
    stage2_queue_lengths: List[int] = field(default_factory=list)

    def summary_statistics(self) -> dict:
        """Calculate comprehensive summary statistics"""
        if not self.end_to_end_times:
            return {}

        import numpy as np

        return {
            # End-to-end metrics
            'mean_end_to_end': np.mean(self.end_to_end_times),
            'p50_end_to_end': np.percentile(self.end_to_end_times, 50),
            'p95_end_to_end': np.percentile(self.end_to_end_times, 95),
            'p99_end_to_end': np.percentile(self.end_to_end_times, 99),

            # Stage 1 metrics
            'mean_stage1_wait': np.mean(self.stage1_wait_times),
            'mean_stage1_service': np.mean(self.stage1_service_times),
            'mean_stage1_response': np.mean(self.stage1_wait_times) + np.mean(self.stage1_service_times),
            'mean_stage1_queue_length': np.mean(self.stage1_queue_lengths) if self.stage1_queue_lengths else 0,

            # Network metrics
            'mean_network_time': np.mean(self.network_times),

            # Stage 2 metrics
            'mean_stage2_wait': np.mean(self.stage2_wait_times),
            'mean_stage2_service': np.mean(self.stage2_service_times),
            'mean_stage2_response': np.mean(self.stage2_wait_times) + np.mean(self.stage2_service_times),
            'mean_stage2_queue_length': np.mean(self.stage2_queue_lengths) if self.stage2_queue_lengths else 0,

            # Throughput
            'throughput': len(self.end_to_end_times) / (max(self.stage2_arrivals) - min(self.stage1_arrivals)) if self.stage1_arrivals and self.stage2_arrivals else 0,

            # Stage 2 arrival rate (should be higher than Stage 1 due to retries)
            'stage1_arrival_rate': len(self.stage1_arrivals) / (max(self.stage1_arrivals) - min(self.stage1_arrivals)) if len(self.stage1_arrivals) > 1 else 0,
            'stage2_arrival_rate': len(self.stage2_arrivals) / (max(self.stage2_arrivals) - min(self.stage2_arrivals)) if len(self.stage2_arrivals) > 1 else 0,
        }


class TandemQueueSystem:
    """
    Two-stage tandem queue system

    Architecture:
        Publishers --λ--> [Stage 1: Broker] --network--> [Stage 2: Receiver] --λ--> Consumers
                          (n₁ servers, μ₁)   (D_link, p)  (n₂ servers, μ₂)

    Key equations:
        Stage 1: ρ₁ = λ/(n₁·μ₁)
        Stage 2: Λ₂ = λ/(1-p)  (HIGHER arrival rate due to retransmissions!)
                 ρ₂ = Λ₂/(n₂·μ₂) = λ/((1-p)·n₂·μ₂)

        Total latency: T = W₁ + S₁ + (2+p)·D_link + W₂ + S₂
    """

    def __init__(self, env: simpy.Environment, config):
        """
        Args:
            env: SimPy environment
            config: TandemQueueConfig with all parameters
        """
        self.env = env
        self.config = config

        # Stage 1: Broker
        self.broker_threads = simpy.Resource(env, capacity=config.n1)
        self.broker_service_rate = config.mu1

        # Network Layer (with callback for Stage 2 arrival tracking)
        self.network = NetworkLayer(
            env=env,
            network_delay=config.network_delay,
            failure_probability=config.failure_prob,
            on_transmission_attempt=self._on_stage2_arrival_attempt
        )

        # Stage 2: Receiver
        self.receiver_threads = simpy.Resource(env, capacity=config.n2)
        self.receiver_service_rate = config.mu2

        # Metrics
        self.metrics = TandemMetrics()

        # Message counter
        self.message_id = 0
        self.messages_in_warmup = 0

    def _on_stage2_arrival_attempt(self, message_id, attempt_num):
        """
        Callback when a transmission attempt is made to Stage 2.
        This tracks the TOTAL arrival rate at Stage 2, including retries.
        This is what makes Λ₂ = λ/(1-p) instead of just λ.
        """
        if not self.is_warmup():
            # Record each transmission attempt as a Stage 2 arrival
            self.metrics.stage2_arrivals.append(self.env.now)

    def is_warmup(self) -> bool:
        """Check if in warmup period"""
        return self.env.now < self.config.warmup_time

    def process_message(self, message_id: int):
        """
        Process message through both stages

        Flow:
        1. Arrive at broker (Stage 1)
        2. Wait in broker queue
        3. Get served by broker
        4. Transmit over network (with possible retries)
        5. Arrive at receiver (Stage 2)
        6. Wait in receiver queue
        7. Get served by receiver
        8. Complete
        """
        # === STAGE 1: BROKER ===
        arrival_time = self.env.now

        # Record arrival at Stage 1
        if not self.is_warmup():
            self.metrics.stage1_arrivals.append(arrival_time)

        # Wait in broker queue
        with self.broker_threads.request() as req:
            stage1_queue_length = len(self.broker_threads.queue)

            yield req

            wait_start = self.env.now
            wait1 = wait_start - arrival_time

            # Service at broker
            service1 = np.random.exponential(1.0 / self.broker_service_rate)
            yield self.env.timeout(service1)

            stage1_complete = self.env.now

        # === NETWORK TRANSMISSION ===
        network_start = self.env.now

        # Transmit with retries (yields internally)
        yield self.env.process(self.network.transmit_message(message_id))

        network_complete = self.env.now
        network_time = network_complete - network_start

        # === STAGE 2: RECEIVER ===
        stage2_arrival = self.env.now

        # Note: Stage 2 arrivals are now tracked in _on_stage2_arrival_attempt callback
        # This happens during network transmission attempts (including retries)
        # So Λ₂ = λ/(1-p) is correctly measured

        # Wait in receiver queue
        with self.receiver_threads.request() as req:
            stage2_queue_length = len(self.receiver_threads.queue)

            yield req

            wait2_start = self.env.now
            wait2 = wait2_start - stage2_arrival

            # Service at receiver
            service2 = np.random.exponential(1.0 / self.receiver_service_rate)
            yield self.env.timeout(service2)

            stage2_complete = self.env.now

        # === COLLECT METRICS (skip warmup) ===
        if not self.is_warmup():
            # End-to-end latency
            total_time = stage2_complete - arrival_time
            self.metrics.end_to_end_times.append(total_time)

            # Stage 1 metrics
            self.metrics.stage1_wait_times.append(wait1)
            self.metrics.stage1_service_times.append(service1)
            self.metrics.stage1_queue_lengths.append(stage1_queue_length)

            # Network metrics
            self.metrics.network_times.append(network_time)

            # Stage 2 metrics
            self.metrics.stage2_wait_times.append(wait2)
            self.metrics.stage2_service_times.append(service2)
            self.metrics.stage2_queue_lengths.append(stage2_queue_length)
        else:
            self.messages_in_warmup += 1

    def message_generator(self):
        """Generate messages with Poisson arrivals at rate λ"""
        while True:
            # Exponential inter-arrival time
            interarrival = np.random.exponential(1.0 / self.config.arrival_rate)
            yield self.env.timeout(interarrival)

            # Create new message
            self.message_id += 1
            self.env.process(self.process_message(self.message_id))

    def run(self) -> Tuple[TandemMetrics, dict]:
        """
        Run tandem queue simulation

        Returns:
            Tuple of (TandemMetrics, network_metrics)
        """
        # Set random seed
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)

        # Start message generator
        self.env.process(self.message_generator())

        # Run simulation
        self.env.run(until=self.config.sim_duration)

        print(f"\nTandem Queue Simulation Complete:")
        print(f"  Total messages: {self.message_id}")
        print(f"  Warmup messages: {self.messages_in_warmup}")
        print(f"  Measured messages: {len(self.metrics.end_to_end_times)}")

        network_metrics = self.network.get_metrics()
        print(f"\nNetwork Metrics:")
        print(f"  Total transmissions: {network_metrics['total_transmissions']}")
        print(f"  Failed transmissions: {network_metrics['failed_transmissions']}")
        print(f"  Average retries: {network_metrics['average_retries_per_message']:.2f}")

        return self.metrics, network_metrics


def run_tandem_simulation(config) -> dict:
    """
    Convenience function to run tandem queue simulation

    Args:
        config: TandemQueueConfig

    Returns:
        Dictionary with simulation results and metrics
    """
    env = simpy.Environment()
    system = TandemQueueSystem(env, config)
    metrics, network_metrics = system.run()

    stats = metrics.summary_statistics()
    stats['network_metrics'] = network_metrics
    stats['config'] = {
        'lambda': config.arrival_rate,
        'n1': config.n1,
        'mu1': config.mu1,
        'n2': config.n2,
        'mu2': config.mu2,
        'network_delay': config.network_delay,
        'failure_prob': config.failure_prob,
    }

    return stats
