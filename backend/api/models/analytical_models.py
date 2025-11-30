"""
Pydantic Models for Analytical API
Request and response models for analytical calculations
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List


class MMNAnalyticalRequest(BaseModel):
    """M/M/N Analytical Calculation Request"""
    arrival_rate: float = Field(..., gt=0, description="Arrival rate λ (messages/sec)")
    num_threads: int = Field(..., gt=0, description="Number of server threads N")
    service_rate: float = Field(..., gt=0, description="Service rate μ (messages/sec/thread)")

    @validator('arrival_rate')
    def validate_stability(cls, v, values):
        """Ensure system is stable (ρ < 1)"""
        if 'num_threads' in values and 'service_rate' in values:
            rho = v / (values['num_threads'] * values['service_rate'])
            if rho >= 1.0:
                raise ValueError(f"System unstable: ρ = {rho:.3f} >= 1.0")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "arrival_rate": 100.0,
                "num_threads": 10,
                "service_rate": 12.0
            }
        }


class MGNAnalyticalRequest(BaseModel):
    """M/G/N Analytical Calculation Request"""
    arrival_rate: float = Field(..., gt=0, description="Arrival rate λ (messages/sec)")
    num_threads: int = Field(..., gt=0, description="Number of server threads N")
    mean_service: float = Field(..., gt=0, description="Mean service time E[S] (seconds)")
    variance_service: float = Field(..., ge=0, description="Service time variance Var(S)")

    class Config:
        json_schema_extra = {
            "example": {
                "arrival_rate": 80.0,
                "num_threads": 10,
                "mean_service": 0.1,
                "variance_service": 0.05
            }
        }


class TandemAnalyticalRequest(BaseModel):
    """Tandem Queue Analytical Calculation Request"""
    arrival_rate: float = Field(..., gt=0, description="Arrival rate λ at Stage 1")
    n1: int = Field(..., gt=0, description="Stage 1 threads")
    mu1: float = Field(..., gt=0, description="Stage 1 service rate")
    n2: int = Field(..., gt=0, description="Stage 2 threads")
    mu2: float = Field(..., gt=0, description="Stage 2 service rate")
    network_delay: float = Field(default=0.01, ge=0, description="Network delay (seconds)")
    failure_prob: float = Field(default=0.0, ge=0.0, lt=1.0, description="Failure probability")

    class Config:
        json_schema_extra = {
            "example": {
                "arrival_rate": 100.0,
                "n1": 10,
                "mu1": 12.0,
                "n2": 12,
                "mu2": 12.0,
                "network_delay": 0.01,
                "failure_prob": 0.2
            }
        }


class AnalyticalResponse(BaseModel):
    """Analytical Calculation Response"""
    model_type: str
    config: Dict[str, Any]
    metrics: Dict[str, float]
    formulas_used: List[str]

    class Config:
        protected_namespaces = ()
        json_schema_extra = {
            "example": {
                "model_type": "M/M/N",
                "config": {
                    "arrival_rate": 100.0,
                    "num_threads": 10,
                    "service_rate": 12.0
                },
                "metrics": {
                    "utilization": 0.833,
                    "erlang_c": 0.456,
                    "mean_waiting_time": 0.045,
                    "mean_queue_length": 4.5,
                    "mean_response_time": 0.128
                },
                "formulas_used": [
                    "Eq. 1: Utilization ρ = λ/(N·μ)",
                    "Eq. 2: Erlang-C formula",
                    "Eq. 5: Mean waiting time Wq"
                ]
            }
        }
