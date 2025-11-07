"""Type-safe configuration using Pydantic"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class QueueConfig(BaseModel):
    """Base configuration for all queue models"""

    # Arrival process
    arrival_rate: float = Field(
        gt=0,
        description="λ (messages/sec)"
    )

    # Service process
    num_threads: int = Field(
        gt=0,
        le=1000,
        description="N (number of threads)"
    )
    service_rate: float = Field(
        gt=0,
        description="μ (messages/sec per thread)"
    )

    # Simulation parameters
    sim_duration: float = Field(
        default=1000.0,
        gt=0,
        description="Simulation time (seconds)"
    )
    warmup_time: float = Field(
        default=100.0,
        ge=0,
        description="Warmup period to discard"
    )
    random_seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducibility"
    )

    @field_validator('service_rate')
    @classmethod
    def check_stability(cls, v, info):
        """Ensure system is stable (ρ < 1)"""
        data = info.data
        if 'arrival_rate' in data and 'num_threads' in data:
            rho = data['arrival_rate'] / (data['num_threads'] * v)
            if rho >= 1.0:
                raise ValueError(
                    f"System unstable: ρ = {rho:.3f} >= 1. "
                    f"Reduce arrival_rate or increase num_threads/service_rate"
                )
        return v

    @property
    def utilization(self) -> float:
        """Calculate ρ = λ/(N·μ)"""
        return self.arrival_rate / (self.num_threads * self.service_rate)

    @property
    def traffic_intensity(self) -> float:
        """Calculate λ/μ"""
        return self.arrival_rate / self.service_rate


class MMNConfig(QueueConfig):
    """M/M/N specific configuration"""
    model_type: Literal["M/M/N"] = "M/M/N"


class MGNConfig(QueueConfig):
    """M/G/N specific configuration

    Note: For Pareto distribution, the scale parameter is automatically
    calculated to match the mean service time (1/service_rate). This ensures
    that different α values are comparable.
    """
    model_type: Literal["M/G/N"] = "M/G/N"

    distribution: Literal["pareto", "lognormal", "weibull"] = Field(
        default="pareto",
        description="Service time distribution"
    )

    # Pareto parameters
    alpha: float = Field(
        default=2.5,
        gt=1.0,
        le=5.0,
        description="Pareto shape parameter"
    )

    @property
    def scale(self) -> float:
        """Calculate Pareto scale parameter to match mean service time

        From E[S] = α·k/(α-1) = 1/μ, we get:
        k = (1/μ) · (α-1)/α

        This ensures all α values have the same mean service time.
        """
        target_mean = 1.0 / self.service_rate  # Desired E[S]
        return target_mean * (self.alpha - 1) / self.alpha

    @property
    def mean_service_time(self) -> float:
        """E[S] = α·k/(α-1)"""
        return (self.alpha * self.scale) / (self.alpha - 1)

    @property
    def variance_service_time(self) -> float:
        """Var[S] for Pareto"""
        if self.alpha <= 2:
            return float('inf')
        return (self.alpha * self.scale**2) / ((self.alpha - 1)**2 * (self.alpha - 2))

    @property
    def coefficient_of_variation(self) -> float:
        """C² = 1/(α(α-2)) for α > 2 (CORRECTED formula)"""
        if self.alpha <= 2:
            return float('inf')
        return 1.0 / (self.alpha * (self.alpha - 2))


class ThreadingConfig(BaseModel):
    """Threading model configuration"""

    model: Literal["dedicated", "shared"] = Field(
        description="Threading model type"
    )

    # Dedicated model
    threads_per_connection: int = Field(
        default=2,
        description="Threads per connection (dedicated model)"
    )

    # Shared model
    overhead_coefficient: float = Field(
        default=0.1,
        ge=0,
        le=0.5,
        description="Overhead factor (shared model)"
    )

    max_connections: Optional[int] = Field(
        default=None,
        description="Maximum concurrent connections"
    )
