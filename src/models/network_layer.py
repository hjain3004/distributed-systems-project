"""
Network Layer Simulation

Models network communication between broker and receiver:
- Network delay (D_link)
- Transmission failures with probability p
- Retransmissions with exponential backoff
"""

import simpy
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class NetworkMetrics:
    """Metrics for network layer"""
    total_transmissions: int = 0
    successful_transmissions: int = 0
    failed_transmissions: int = 0
    total_retries: int = 0

    @property
    def failure_rate(self) -> float:
        """Actual failure rate observed"""
        if self.total_transmissions == 0:
            return 0.0
        return self.failed_transmissions / self.total_transmissions

    @property
    def average_retries(self) -> float:
        """Average retries per message"""
        if self.successful_transmissions == 0:
            return 0.0
        return self.total_retries / self.successful_transmissions


class NetworkLayer:
    """
    Simulates network communication with delays and failures

    Based on Li et al. (2015) model:
    - Messages sent from broker to receiver
    - Network delay D_link for each transmission
    - Probability p of transmission failure
    - Failed transmissions are retried
    - ACK/NACK sent back (also takes D_link)
    """

    def __init__(self, env: simpy.Environment,
                 network_delay: float,
                 failure_probability: float,
                 max_retries: int = 10,
                 on_transmission_attempt=None):
        """
        Args:
            env: SimPy environment
            network_delay: One-way network delay D_link (seconds)
            failure_probability: Probability p of transmission failure (0 ≤ p < 1)
            max_retries: Maximum retransmission attempts
            on_transmission_attempt: Optional callback(message_id, attempt_num) called for each transmission attempt
        """
        self.env = env
        self.network_delay = network_delay
        self.failure_probability = failure_probability
        self.max_retries = max_retries
        self.on_transmission_attempt = on_transmission_attempt

        # Metrics
        self.metrics = NetworkMetrics()

    def transmit_message(self, message_id: int):
        """
        Transmit message from broker to receiver with retries

        Returns:
            Generator for SimPy process (total time including retries)
        """
        retries = 0

        while retries <= self.max_retries:
            # === SEND: Broker → Receiver ===
            yield self.env.timeout(self.network_delay)

            self.metrics.total_transmissions += 1

            # Notify callback of transmission attempt (for Stage 2 arrival tracking)
            if self.on_transmission_attempt is not None:
                self.on_transmission_attempt(message_id, retries)

            # Check if transmission succeeds
            if np.random.random() > self.failure_probability:
                # SUCCESS!
                self.metrics.successful_transmissions += 1

                # ACK: Receiver → Broker (also takes D_link)
                yield self.env.timeout(self.network_delay)

                # Record retries for this message
                if retries > 0:
                    self.metrics.total_retries += retries

                return  # Message delivered successfully

            else:
                # FAILURE - transmission lost
                self.metrics.failed_transmissions += 1

                # NACK/Timeout: Receiver → Broker
                yield self.env.timeout(self.network_delay)

                retries += 1

        # Max retries exceeded - message lost (should rarely happen)
        raise RuntimeError(f"Message {message_id} failed after {self.max_retries} retries")

    def get_metrics(self) -> dict:
        """Get network layer metrics"""
        return {
            'total_transmissions': self.metrics.total_transmissions,
            'successful_transmissions': self.metrics.successful_transmissions,
            'failed_transmissions': self.metrics.failed_transmissions,
            'total_retries': self.metrics.total_retries,
            'observed_failure_rate': self.metrics.failure_rate,
            'average_retries_per_message': self.metrics.average_retries,
        }
