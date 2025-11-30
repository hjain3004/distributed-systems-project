"""
Pydantic Models for Distributed Systems API
Request and response models for Raft, Vector Clocks, and 2PC
"""

from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime


class RaftRequest(BaseModel):
    """Raft Consensus Simulation Request"""
    num_nodes: int = Field(default=5, ge=3, description="Number of nodes in the cluster (must be >= 3)")
    simulation_time: float = Field(default=50.0, gt=0, description="Simulation duration (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "num_nodes": 5,
                "simulation_time": 50.0
            }
        }


class VectorClockRequest(BaseModel):
    """Vector Clock Simulation Request"""
    num_processes: int = Field(default=3, ge=2, description="Number of processes")

    class Config:
        json_schema_extra = {
            "example": {
                "num_processes": 3
            }
        }


class TwoPhaseCommitRequest(BaseModel):
    """Two-Phase Commit Simulation Request"""
    num_participants: int = Field(default=5, ge=2, description="Number of participants")
    vote_yes_probability: float = Field(default=1.0, ge=0.0, le=1.0, description="Probability of voting YES (0-1)")
    simulation_time: float = Field(default=100.0, gt=0, description="Simulation duration (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "num_participants": 5,
                "vote_yes_probability": 1.0,
                "simulation_time": 100.0
            }
        }


class DistributedSimulationResponse(BaseModel):
    """Distributed Systems Simulation Response"""
    simulation_id: str
    protocol: str  # Raft, Vector Clocks, Two-Phase Commit
    results: Dict[str, Any]
    message: str
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "simulation_id": "123e4567-e89b-12d3-a456-426614174000",
                "protocol": "Raft",
                "results": {
                    "leader_node_id": 2,
                    "num_nodes": 5,
                    "leader_elected": True
                },
                "message": "Raft consensus simulation completed successfully",
                "created_at": "2025-11-17T12:00:00"
            }
        }
