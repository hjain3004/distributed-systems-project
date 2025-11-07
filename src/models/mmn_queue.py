"""M/M/N queue implementation"""

import numpy as np
import simpy
from .base import QueueModel
from ..core.config import MMNConfig
from ..core.metrics import SimulationMetrics


class MMNQueue(QueueModel):
    """
    M/M/N Queue Model

    - M: Markovian (Poisson) arrivals
    - M: Markovian (exponential) service times
    - N: Multiple servers (threads)
    """

    def __init__(self, env: simpy.Environment, config: MMNConfig):
        super().__init__(env, config)
        self.service_rate = config.service_rate

    def model_name(self) -> str:
        return f"M/M/{self.config.num_threads}"

    def get_service_time(self) -> float:
        """
        Exponential service time: f(t) = μ·e^(-μt)

        Mean = 1/μ, Variance = 1/μ², CV² = 1
        """
        return np.random.exponential(1.0 / self.service_rate)


def run_mmn_simulation(config: MMNConfig) -> SimulationMetrics:
    """
    Convenience function to run M/M/N simulation

    Args:
        config: M/M/N configuration

    Returns:
        SimulationMetrics with results
    """
    env = simpy.Environment()
    model = MMNQueue(env, config)
    return model.run()
