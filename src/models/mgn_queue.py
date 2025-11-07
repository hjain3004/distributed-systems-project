"""M/G/N queue implementation with heavy-tailed service times"""

import simpy
from .base import QueueModel
from ..core.config import MGNConfig
from ..core.distributions import create_distribution, ServiceTimeDistribution
from ..core.metrics import SimulationMetrics


class MGNQueue(QueueModel):
    """
    M/G/N Queue Model

    - M: Markovian (Poisson) arrivals
    - G: General service time distribution
    - N: Multiple servers (threads)
    """

    def __init__(self, env: simpy.Environment, config: MGNConfig):
        super().__init__(env, config)

        # Create service time distribution
        self.service_dist: ServiceTimeDistribution = create_distribution(config)

    def model_name(self) -> str:
        dist_name = self.config.distribution
        if dist_name == "pareto":
            return f"M/Pareto(α={self.config.alpha})/{self.config.num_threads}"
        else:
            return f"M/{dist_name}/{self.config.num_threads}"

    def get_service_time(self) -> float:
        """
        Sample from general distribution (e.g., Pareto)

        For Pareto: f(t) = α·k^α / t^(α+1)
        Mean = α·k/(α-1), heavy-tailed for small α
        """
        return self.service_dist.sample()


def run_mgn_simulation(config: MGNConfig) -> SimulationMetrics:
    """
    Convenience function to run M/G/N simulation

    Args:
        config: M/G/N configuration

    Returns:
        SimulationMetrics with results
    """
    env = simpy.Environment()
    model = MGNQueue(env, config)
    return model.run()
