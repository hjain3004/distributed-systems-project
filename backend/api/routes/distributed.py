"""
Distributed Systems Routes
Endpoints for Raft consensus, Vector Clocks, and Two-Phase Commit simulations
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid
from datetime import datetime
import sys
import os
# Add both project root and backend directory to path
# Add project root to path
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
project_root = os.path.dirname(backend_dir)
sys.path.append(project_root)
sys.path.append(backend_dir)

from api.models.distributed_models import (
    RaftRequest,
    VectorClockRequest,
    TwoPhaseCommitRequest,
    DistributedSimulationResponse
)

router = APIRouter()


@router.post("/raft", response_model=DistributedSimulationResponse)
async def run_raft_simulation(request: RaftRequest):
    """
    Run Raft consensus simulation

    Simulates leader election and log replication across N nodes

    Returns:
    - Leader node ID
    - Election rounds
    - Log replication status
    - Consensus timeline
    """
    try:
        import simpy
        from src.models.raft_consensus import RaftCluster

        # Create simulation environment
        env = simpy.Environment()

        # Create Raft cluster
        cluster = RaftCluster(
            env=env,
            num_nodes=request.num_nodes
        )

        # Run simulation
        env.run(until=request.simulation_time)

        # Get leader
        leader = cluster.get_leader()

        # Collect metrics
        results = {
            "leader_node_id": leader.node_id if leader else None,
            "num_nodes": request.num_nodes,
            "simulation_time": request.simulation_time,
            "leader_elected": leader is not None,
            "total_elections": len([n for n in cluster.nodes if n.role == "leader"]),
            "nodes_status": [
                {
                    "node_id": node.node_id,
                    "role": node.role,
                    "term": node.current_term,
                    "voted_for": node.voted_for,
                    "log_length": len(node.log)
                }
                for node in cluster.nodes
            ]
        }

        return DistributedSimulationResponse(
            simulation_id=str(uuid.uuid4()),
            protocol="Raft",
            results=results,
            message="Raft consensus simulation completed successfully",
            created_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vector-clocks", response_model=DistributedSimulationResponse)
async def run_vector_clock_simulation(request: VectorClockRequest):
    """
    Run Vector Clock causality tracking simulation

    Demonstrates happened-before relationships in distributed events

    Returns:
    - Event timeline
    - Vector clock states
    - Causality relationships
    """
    try:
        from src.models.vector_clocks import CausalityTracker

        # Create tracker
        tracker = CausalityTracker(num_processes=request.num_processes)

        # Simulate events based on request
        events = []

        # Generate local events
        for proc_id in range(request.num_processes):
            for i in range(3):  # 3 local events per process
                vc = tracker.local_event(proc_id)
                events.append({
                    "type": "local",
                    "process": proc_id,
                    "vector_clock": vc.clocks.copy()
                })

        # Generate send/receive events
        vc1 = tracker.send_event(0)
        events.append({"type": "send", "process": 0, "vector_clock": vc1.clocks.copy()})

        vc2 = tracker.receive_event(1, vc1)
        events.append({"type": "receive", "process": 1, "vector_clock": vc2.clocks.copy()})

        # Check causality
        relationship = tracker.check_causality(0, 1)

        results = {
            "num_processes": request.num_processes,
            "events": events,
            "causality_example": {
                "event_a": {"process": 0, "clock": vc1.clocks.copy()},
                "event_b": {"process": 1, "clock": vc2.clocks.copy()},
                "relationship": relationship
            },
            "total_events": len(events)
        }

        return DistributedSimulationResponse(
            simulation_id=str(uuid.uuid4()),
            protocol="Vector Clocks",
            results=results,
            message="Vector clock simulation completed successfully",
            created_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/two-phase-commit", response_model=DistributedSimulationResponse)
async def run_2pc_simulation(request: TwoPhaseCommitRequest):
    """
    Run Two-Phase Commit protocol simulation

    Simulates atomic commit across multiple participants

    Returns:
    - Commit/abort decision
    - Participant votes
    - Protocol phases timeline
    - Success rate
    """
    try:
        import simpy
        from src.models.two_phase_commit import TwoPhaseCommitCluster

        # Create simulation environment
        env = simpy.Environment()

        # Create 2PC cluster
        cluster = TwoPhaseCommitCluster(
            env=env,
            num_participants=request.num_participants,
            vote_yes_prob=request.vote_yes_probability
        )

        # Run simulation
        env.run(until=request.simulation_time)

        # Get metrics from coordinator
        metrics = cluster.coordinator.get_metrics()

        results = {
            "num_participants": request.num_participants,
            "vote_yes_probability": request.vote_yes_probability,
            "simulation_time": request.simulation_time,
            "total_transactions": metrics["total_transactions"],
            "committed": metrics["committed"],
            "aborted": metrics["aborted"],
            "commit_rate": metrics["commit_rate"],
            "transactions": cluster.coordinator.transactions[:10]  # First 10 transactions
        }

        return DistributedSimulationResponse(
            simulation_id=str(uuid.uuid4()),
            protocol="Two-Phase Commit",
            results=results,
            message="2PC simulation completed successfully",
            created_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/protocols")
async def list_protocols():
    """List all available distributed systems protocols"""
    return {
        "protocols": [
            {
                "name": "Raft",
                "description": "Consensus algorithm for leader election and log replication",
                "endpoint": "/api/distributed/raft"
            },
            {
                "name": "Vector Clocks",
                "description": "Causality tracking in distributed systems",
                "endpoint": "/api/distributed/vector-clocks"
            },
            {
                "name": "Two-Phase Commit",
                "description": "Atomic commit protocol for distributed transactions",
                "endpoint": "/api/distributed/two-phase-commit"
            }
        ]
    }
