"""Abstract base class for queue models"""

from abc import ABC, abstractmethod
import simpy
import numpy as np
from typing import List, Optional
from ..core.config import QueueConfig
from ..core.metrics import SimulationMetrics


class QueueModel(ABC):
    """Abstract base class for all queue models"""

    def __init__(self, env: simpy.Environment, config: QueueConfig):
        self.env = env
        self.config = config
        self.metrics = SimulationMetrics(
            model_name=self.model_name(),
            config=vars(config)
        )

        # Thread pool (SimPy Resource)
        self.threads = simpy.Resource(env, capacity=config.num_threads)

        # Message counter
        self.message_id = 0
        self.messages_in_warmup = 0

    @abstractmethod
    def model_name(self) -> str:
        """Return model name for identification"""
        pass

    @abstractmethod
    def get_service_time(self) -> float:
        """Generate service time sample"""
        pass

    def is_warmup(self) -> bool:
        """Check if in warmup period"""
        return self.env.now < self.config.warmup_time

    def process_message(self, message_id: int):
        """
        Process a single message through the queue

        This is the core queueing process:
        1. Message arrives
        2. Waits for available thread
        3. Gets served
        4. Departs
        """
        arrival_time = self.env.now

        # Record queue length at arrival
        queue_length = len(self.threads.queue)

        # Request a thread from the pool
        with self.threads.request() as request:
            yield request

            # Thread acquired - calculate waiting time
            wait_time = self.env.now - arrival_time

            # Generate service time
            service_time = self.get_service_time()

            # Serve the message
            yield self.env.timeout(service_time)

            # Message departs
            departure_time = self.env.now

            # Collect metrics (skip warmup period)
            if not self.is_warmup():
                self.metrics.arrival_times.append(arrival_time)
                self.metrics.wait_times.append(wait_time)
                self.metrics.service_times.append(service_time)
                self.metrics.queue_lengths.append(queue_length)
                self.metrics.departure_times.append(departure_time)
            else:
                self.messages_in_warmup += 1

    def message_generator(self):
        """
        Generate messages with Poisson arrivals

        Poisson process: inter-arrival times are exponential
        """
        while True:
            # Exponential inter-arrival time
            interarrival = np.random.exponential(1.0 / self.config.arrival_rate)
            yield self.env.timeout(interarrival)

            # Create new message
            self.message_id += 1
            self.env.process(self.process_message(self.message_id))

    def run(self) -> SimulationMetrics:
        """
        Run the simulation

        Returns:
            SimulationMetrics with collected data
        """
        # Set random seed if provided
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)

        # Start message generator
        self.env.process(self.message_generator())

        # Run simulation
        self.env.run(until=self.config.sim_duration)

        print(f"Simulation complete:")
        print(f"  Model: {self.model_name()}")
        print(f"  Total messages: {self.message_id}")
        print(f"  Warmup messages: {self.messages_in_warmup}")
        print(f"  Measured messages: {len(self.metrics.wait_times)}")

        return self.metrics
