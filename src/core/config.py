"""Type-safe configuration using Pydantic"""

from pydantic import BaseModel, Field, field_validator, model_validator
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


class TandemQueueConfig(BaseModel):
    """
    Configuration for two-stage tandem queue (Li et al. 2015)

    Models:
        Publisher → [Stage 1: Broker] → Network → [Stage 2: Receiver] → Consumer
                    (n₁ servers, μ₁)    (D, p)    (n₂ servers, μ₂)

    Key formulas:
        Stage 1: ρ₁ = λ/(n₁·μ₁)
        Stage 2: Λ₂ = λ/(1-p)  ← CRITICAL: Higher due to retransmissions!
                 ρ₂ = Λ₂/(n₂·μ₂) = λ/((1-p)·n₂·μ₂)
    """
    model_type: Literal["Tandem"] = "Tandem"

    # Arrival process
    arrival_rate: float = Field(
        gt=0,
        description="λ (messages/sec)"
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

    # Stage 1: Broker
    n1: int = Field(
        gt=0,
        le=100,
        description="Number of broker threads (Stage 1)"
    )
    mu1: float = Field(
        gt=0,
        description="Broker service rate (messages/sec/thread)"
    )

    # Stage 2: Receiver
    n2: int = Field(
        gt=0,
        le=100,
        description="Number of receiver threads (Stage 2)"
    )
    mu2: float = Field(
        gt=0,
        description="Receiver service rate (messages/sec/thread)"
    )

    # Network parameters
    network_delay: float = Field(
        gt=0,
        description="One-way network delay D_link (seconds)"
    )
    failure_prob: float = Field(
        ge=0,
        lt=1.0,
        description="Transmission failure probability p (0 ≤ p < 1)"
    )

    @model_validator(mode='after')
    def check_stage2_stability(self):
        """
        Ensure Stage 2 is stable

        CRITICAL: Stage 2 arrival rate is Λ₂ = λ/(1-p), NOT λ!
        """
        # Effective arrival rate at Stage 2 (includes retries)
        Lambda2 = self.arrival_rate / (1 - self.failure_prob)

        # Stage 2 utilization
        rho2 = Lambda2 / (self.n2 * self.mu2)

        if rho2 >= 1.0:
            raise ValueError(
                f"Stage 2 unstable: ρ₂ = {rho2:.3f} >= 1. "
                f"Λ₂ = λ/(1-p) = {Lambda2:.1f} msg/sec. "
                f"Reduce arrival_rate or failure_prob, or increase n2/mu2."
            )

        return self

    @property
    def stage1_utilization(self) -> float:
        """ρ₁ = λ/(n₁·μ₁)"""
        return self.arrival_rate / (self.n1 * self.mu1)

    @property
    def stage2_effective_arrival(self) -> float:
        """
        Effective arrival rate at Stage 2 (includes retransmissions)

        Λ₂ = λ/(1-p)

        When p=0 (no failures): Λ₂ = λ
        When p=0.2 (20% failures): Λ₂ = 1.25λ (25% higher!)
        """
        return self.arrival_rate / (1 - self.failure_prob)

    @property
    def stage2_utilization(self) -> float:
        """
        ρ₂ = Λ₂/(n₂·μ₂) = λ/((1-p)·n₂·μ₂)

        Note: Stage 2 utilization is HIGHER than Stage 1 when p > 0!
        """
        return self.stage2_effective_arrival / (self.n2 * self.mu2)

    @property
    def expected_network_time(self) -> float:
        """
        Expected network time including retries

        E[Network Time] = (2 + p) · D_link

        Components:
        - 2·D_link: Initial send + ACK
        - p·D_link: Average retries (p failures × D_link per retry)
        """
        return (2 + self.failure_prob) * self.network_delay
