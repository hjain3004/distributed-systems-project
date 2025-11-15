"""Type-safe configuration using Pydantic"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional, List, Dict


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


class PriorityQueueConfig(QueueConfig):
    """
    Priority Queue Configuration (M/M/N with priorities)

    Models a queue with multiple priority classes.
    Higher priority messages are served before lower priority messages.

    Example:
        config = PriorityQueueConfig(
            arrival_rate=100,
            num_threads=10,
            service_rate=12,
            num_priorities=3,
            priority_rates=[30, 50, 20],  # High, Medium, Low
            preemptive=False
        )
    """
    model_type: Literal["Priority"] = "Priority"

    num_priorities: int = Field(
        default=2,
        gt=0,
        le=10,
        description="Number of priority classes (1 = highest)"
    )

    priority_rates: List[float] = Field(
        default=[],
        description="Arrival rates for each priority class (must sum to arrival_rate)"
    )

    preemptive: bool = Field(
        default=False,
        description="Whether higher priority can preempt lower priority service"
    )

    @model_validator(mode='after')
    def validate_priority_rates(self):
        """Ensure priority rates sum to total arrival rate"""
        if not self.priority_rates:
            # Auto-distribute evenly if not specified
            rate_per_class = self.arrival_rate / self.num_priorities
            self.priority_rates = [rate_per_class] * self.num_priorities

        if len(self.priority_rates) != self.num_priorities:
            raise ValueError(
                f"priority_rates length ({len(self.priority_rates)}) "
                f"must match num_priorities ({self.num_priorities})"
            )

        total_rate = sum(self.priority_rates)
        if abs(total_rate - self.arrival_rate) > 0.01:
            raise ValueError(
                f"priority_rates sum ({total_rate:.2f}) must equal "
                f"arrival_rate ({self.arrival_rate:.2f})"
            )

        return self

    @property
    def priority_utilizations(self) -> List[float]:
        """Calculate utilization for each priority class"""
        return [rate / (self.num_threads * self.service_rate)
                for rate in self.priority_rates]


class FiniteCapacityConfig(QueueConfig):
    """
    Finite Capacity Queue Configuration (M/M/N/K)

    Models a queue with maximum capacity K.
    When queue is full, new arrivals are blocked/rejected.

    Example:
        config = FiniteCapacityConfig(
            arrival_rate=100,
            num_threads=10,
            service_rate=12,
            max_capacity=50,
            blocking_strategy='reject'
        )
    """
    model_type: Literal["FiniteCapacity"] = "FiniteCapacity"

    max_capacity: int = Field(
        gt=0,
        le=10000,
        description="Maximum queue capacity K (including those in service)"
    )

    blocking_strategy: Literal["reject", "wait"] = Field(
        default="reject",
        description="What to do when queue is full: reject or wait for space"
    )

    @field_validator('service_rate')
    @classmethod
    def skip_stability_check(cls, v, info):
        """
        Finite capacity queues don't need stability check

        With finite capacity, the system is always stable even if λ > N·μ
        (arrivals are simply blocked when full)
        """
        return v

    @property
    def max_queue_length(self) -> int:
        """Maximum number of messages waiting (excluding those in service)"""
        return max(0, self.max_capacity - self.num_threads)


class ThreadingConfig(BaseModel):
    """Threading model configuration"""

    model: Literal["dedicated", "shared"] = Field(
        default="shared",
        description="Threading model type"
    )

    # Shared thread pool parameters
    num_threads: int = Field(
        default=100,
        gt=0,
        description="Total threads in pool"
    )
    context_switch_overhead: float = Field(
        default=0.0001,
        ge=0,
        description="Context switch overhead (seconds)"
    )

    # Dedicated (thread-per-connection) parameters
    threads_per_connection: int = Field(
        default=2,
        gt=0,
        description="Threads per connection (dedicated model)"
    )

    @property
    def max_connections_dedicated(self) -> int:
        """Maximum concurrent connections (dedicated model)"""
        if self.model == "dedicated":
            return self.num_threads // self.threads_per_connection
        return 0


class MEkNConfig(QueueConfig):
    """M/Ek/N specific configuration (Erlang-k service)"""
    model_type: Literal["M/Ek/N"] = "M/Ek/N"

    erlang_k: int = Field(
        default=2,
        gt=0,
        le=20,
        description="Number of Erlang phases (k)"
    )


class TandemQueueConfig(BaseModel):
    """
    Tandem (two-stage) queue configuration

    Models message broker → network → receiver architecture from Li et al. (2015)
    """

    # Arrival process
    arrival_rate: float = Field(
        gt=0,
        description="λ (messages/sec arriving at Stage 1)"
    )

    # Simulation parameters
    sim_duration: float = Field(
        default=1000.0,
        gt=0
    )
    warmup_time: float = Field(
        default=100.0,
        ge=0
    )
    random_seed: Optional[int] = Field(
        default=None
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
