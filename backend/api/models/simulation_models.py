"""
Pydantic Models for Simulation API
Request and response models for queue simulations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime


class MMNSimulationRequest(BaseModel):
    """M/M/N Queue Simulation Request"""
    arrival_rate: float = Field(..., gt=0, description="Arrival rate λ (messages/sec)")
    num_threads: int = Field(..., gt=0, description="Number of server threads N")
    service_rate: float = Field(..., gt=0, description="Service rate μ (messages/sec/thread)")
    sim_duration: float = Field(default=1000.0, gt=0, description="Simulation duration (seconds)")
    warmup_time: float = Field(default=100.0, ge=0, description="Warmup period to discard (seconds)")
    random_seed: Optional[int] = Field(default=42, description="Random seed for reproducibility")

    @validator('arrival_rate')
    def validate_stability(cls, v, values):
        """Ensure system is stable (ρ < 1)"""
        if 'num_threads' in values and 'service_rate' in values:
            rho = v / (values['num_threads'] * values['service_rate'])
            if rho >= 1.0:
                raise ValueError(f"System unstable: ρ = {rho:.3f} >= 1.0. Reduce arrival_rate or increase num_threads/service_rate")
        return v

    class Config:
        schema_extra = {
            "example": {
                "arrival_rate": 100.0,
                "num_threads": 10,
                "service_rate": 12.0,
                "sim_duration": 1000.0,
                "warmup_time": 100.0,
                "random_seed": 42
            }
        }


class MGNSimulationRequest(BaseModel):
    """M/G/N Queue Simulation Request (Heavy-tailed distributions)"""
    arrival_rate: float = Field(..., gt=0, description="Arrival rate λ (messages/sec)")
    num_threads: int = Field(..., gt=0, description="Number of server threads N")
    service_rate: float = Field(..., gt=0, description="Mean service rate μ (messages/sec/thread)")
    distribution: str = Field(default="pareto", description="Service time distribution (pareto, lognormal, exponential)")
    alpha: float = Field(default=2.5, gt=1.0, description="Pareto shape parameter (α > 1 for finite mean)")
    sim_duration: float = Field(default=1000.0, gt=0, description="Simulation duration (seconds)")
    warmup_time: float = Field(default=100.0, ge=0, description="Warmup period to discard (seconds)")
    random_seed: Optional[int] = Field(default=42, description="Random seed")

    @validator('distribution')
    def validate_distribution(cls, v):
        allowed = ["pareto", "lognormal", "exponential"]
        if v not in allowed:
            raise ValueError(f"Distribution must be one of: {allowed}")
        return v

    @validator('alpha')
    def validate_alpha(cls, v):
        """Warn about infinite variance when α < 2"""
        if v < 2.0:
            # Allow but warn (infinite variance)
            pass
        return v

    class Config:
        schema_extra = {
            "example": {
                "arrival_rate": 80.0,
                "num_threads": 10,
                "service_rate": 10.0,
                "distribution": "pareto",
                "alpha": 2.5,
                "sim_duration": 1000.0,
                "warmup_time": 100.0,
                "random_seed": 42
            }
        }


class TandemSimulationRequest(BaseModel):
    """Tandem Queue (Two-Stage) Simulation Request"""
    arrival_rate: float = Field(..., gt=0, description="Arrival rate λ at Stage 1 (messages/sec)")
    n1: int = Field(..., gt=0, description="Stage 1 (broker) number of threads")
    mu1: float = Field(..., gt=0, description="Stage 1 service rate (messages/sec/thread)")
    n2: int = Field(..., gt=0, description="Stage 2 (receiver) number of threads")
    mu2: float = Field(..., gt=0, description="Stage 2 service rate (messages/sec/thread)")
    network_delay: float = Field(default=0.01, ge=0, description="Network propagation delay (seconds)")
    failure_prob: float = Field(default=0.0, ge=0.0, le=1.0, description="Transmission failure probability (0-1)")
    sim_duration: float = Field(default=1000.0, gt=0, description="Simulation duration (seconds)")
    warmup_time: float = Field(default=100.0, ge=0, description="Warmup period (seconds)")
    random_seed: Optional[int] = Field(default=42, description="Random seed")

    @validator('failure_prob')
    def validate_failure_prob(cls, v, values):
        """Check Stage 2 stability with load amplification"""
        if v >= 1.0:
            raise ValueError("failure_prob must be < 1.0")

        # Check Stage 2 utilization: ρ₂ = λ/((1-p)·n₂·μ₂)
        if 'arrival_rate' in values and 'n2' in values and 'mu2' in values:
            lambda2 = values['arrival_rate'] / (1 - v) if v < 1.0 else float('inf')
            rho2 = lambda2 / (values['n2'] * values['mu2'])
            if rho2 >= 1.0:
                raise ValueError(
                    f"Stage 2 unstable: ρ₂ = {rho2:.3f} >= 1.0 "
                    f"(effective arrival rate Λ₂ = {lambda2:.1f} msg/sec). "
                    f"Increase n2 or mu2, or reduce failure_prob"
                )
        return v

    class Config:
        schema_extra = {
            "example": {
                "arrival_rate": 100.0,
                "n1": 10,
                "mu1": 12.0,
                "n2": 12,
                "mu2": 12.0,
                "network_delay": 0.01,
                "failure_prob": 0.2,
                "sim_duration": 1000.0,
                "warmup_time": 100.0,
                "random_seed": 42
            }
        }


class SimulationResponse(BaseModel):
    """Generic Simulation Response"""
    simulation_id: str
    status: str  # running, completed, failed
    model_type: str  # M/M/N, M/G/N, Tandem, etc.
    message: str
    created_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "simulation_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "running",
                "model_type": "M/M/N",
                "message": "Simulation started successfully",
                "created_at": "2025-11-17T12:00:00"
            }
        }


class SimulationStatus(BaseModel):
    """Simulation Status Response"""
    simulation_id: str
    status: str
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage")
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "simulation_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "running",
                "progress": 45.5,
                "message": "Processing...",
                "started_at": "2025-11-17T12:00:00",
                "completed_at": None
            }
        }
