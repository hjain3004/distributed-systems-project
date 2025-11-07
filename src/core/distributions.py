"""Service time distribution implementations"""

from abc import ABC, abstractmethod
import numpy as np
from scipy import stats
from typing import Protocol


class ServiceTimeDistribution(Protocol):
    """Protocol for service time distributions"""

    def sample(self) -> float:
        """Generate one service time sample"""
        ...

    def mean(self) -> float:
        """Return E[S]"""
        ...

    def variance(self) -> float:
        """Return Var[S]"""
        ...

    def coefficient_of_variation(self) -> float:
        """Return C² = Var[S]/E[S]²"""
        ...


class ExponentialService:
    """Exponential service time (M/M/N)"""

    def __init__(self, rate: float):
        """
        Args:
            rate: μ (messages/sec per thread)
        """
        self.rate = rate  # μ
        self._dist = stats.expon(scale=1/rate)

    def sample(self) -> float:
        return self._dist.rvs()

    def mean(self) -> float:
        return 1.0 / self.rate

    def variance(self) -> float:
        return 1.0 / (self.rate ** 2)

    def coefficient_of_variation(self) -> float:
        return 1.0  # Always 1 for exponential


class ParetoService:
    """Pareto (heavy-tailed) service time

    Implements Equation 6 from the project plan:
    f(t) = α·k^α / t^(α+1) for t ≥ k
    """

    def __init__(self, alpha: float, scale: float):
        """
        Args:
            alpha: Shape parameter (α > 1)
            scale: Scale parameter (k > 0, minimum value)
        """
        if alpha <= 1:
            raise ValueError("alpha must be > 1")

        self.alpha = alpha
        self.scale = scale

    def sample(self) -> float:
        """Sample using inverse transform method

        Pareto CDF: F(t) = 1 - (k/t)^α
        Inverse CDF: F^(-1)(u) = k / (1-u)^(1/α)

        This ensures correct statistical properties.
        """
        u = np.random.uniform(0, 1)
        return self.scale / ((1 - u) ** (1.0 / self.alpha))

    def mean(self) -> float:
        """
        Equation 7: E[S] = α·k/(α-1)
        """
        return (self.alpha * self.scale) / (self.alpha - 1)

    def variance(self) -> float:
        """
        Equation 8: Var[S] = α·k²/((α-1)²·(α-2)) for α > 2
        """
        if self.alpha <= 2:
            return float('inf')
        numerator = self.alpha * (self.scale ** 2)
        denominator = ((self.alpha - 1) ** 2) * (self.alpha - 2)
        return numerator / denominator

    def coefficient_of_variation(self) -> float:
        """
        Equation 9 (CORRECTED): C² = 1/(α(α-2)) for α > 2

        Derived from: CV² = Var[S]/(E[S])²
        where Var[S] = α·k²/((α-1)²(α-2)) and E[S] = α·k/(α-1)

        Note: The original equation had an error. The correct formula
        includes the α term in the denominator.
        """
        if self.alpha <= 2:
            return float('inf')
        return 1.0 / (self.alpha * (self.alpha - 2))


class LognormalService:
    """Lognormal service time (alternative heavy-tail)"""

    def __init__(self, mu: float, sigma: float):
        """
        Args:
            mu: Location parameter
            sigma: Scale parameter
        """
        self.mu = mu
        self.sigma = sigma
        self._dist = stats.lognorm(s=sigma, scale=np.exp(mu))

    def sample(self) -> float:
        return self._dist.rvs()

    def mean(self) -> float:
        return np.exp(self.mu + self.sigma**2 / 2)

    def variance(self) -> float:
        exp_sigma2 = np.exp(self.sigma**2)
        return (exp_sigma2 - 1) * np.exp(2*self.mu + self.sigma**2)

    def coefficient_of_variation(self) -> float:
        return np.exp(self.sigma**2) - 1


class WeibullService:
    """Weibull service time distribution"""

    def __init__(self, shape: float, scale: float):
        """
        Args:
            shape: Shape parameter (k)
            scale: Scale parameter (λ)
        """
        self.shape = shape
        self.scale = scale
        self._dist = stats.weibull_min(c=shape, scale=scale)

    def sample(self) -> float:
        return self._dist.rvs()

    def mean(self) -> float:
        from scipy.special import gamma
        return self.scale * gamma(1 + 1/self.shape)

    def variance(self) -> float:
        from scipy.special import gamma
        mean = self.mean()
        second_moment = (self.scale ** 2) * gamma(1 + 2/self.shape)
        return second_moment - mean**2

    def coefficient_of_variation(self) -> float:
        return self.variance() / (self.mean() ** 2)


def create_distribution(config) -> ServiceTimeDistribution:
    """Factory function to create distribution from config

    Args:
        config: MGNConfig object with distribution parameters

    Returns:
        ServiceTimeDistribution instance
    """
    if config.distribution == "pareto":
        return ParetoService(alpha=config.alpha, scale=config.scale)

    elif config.distribution == "lognormal":
        # Derive mu, sigma to match desired mean service time
        target_mean = 1.0 / config.service_rate
        cv_squared = config.coefficient_of_variation if hasattr(config, 'coefficient_of_variation') else 1.0
        sigma = np.sqrt(np.log(1 + cv_squared))
        mu = np.log(target_mean) - sigma**2 / 2
        return LognormalService(mu=mu, sigma=sigma)

    elif config.distribution == "weibull":
        # Use shape parameter to control variability
        shape = 2.0  # Default shape
        scale = 1.0 / config.service_rate
        return WeibullService(shape=shape, scale=scale)

    else:
        raise ValueError(f"Unknown distribution: {config.distribution}")
