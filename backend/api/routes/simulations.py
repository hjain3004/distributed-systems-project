"""
Simulation Routes
Endpoints for running queue simulations (M/M/N, M/G/N, Tandem, etc.)
Includes WebSocket support for real-time progress updates
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from typing import Dict, Any, Optional
import asyncio
import json
from datetime import datetime
import uuid

# Import existing simulation modules
import sys
import os
# Add both project root and backend directory to path
sys.path.append('/home/user/distributed-systems-project')
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from src.core.config import MMNConfig, MGNConfig, TandemQueueConfig, HeterogeneousMMNConfig, ServerGroup
from src.models.mmn_queue import run_mmn_simulation
from src.models.mgn_queue import run_mgn_simulation
from src.models.tandem_queue import run_tandem_simulation

from api.models.simulation_models import (
    MMNSimulationRequest,
    MGNSimulationRequest,
    TandemSimulationRequest,
    HeterogeneousSimulationRequest,
    DistributedSimulationRequest,
    SimulationResponse,
    SimulationStatus
)
from api.services.simulation_service import SimulationService

router = APIRouter()

# Simulation service (in-memory storage for demo)
simulation_service = SimulationService()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@router.post("/mmn", response_model=SimulationResponse)
async def run_mmn(request: MMNSimulationRequest, background_tasks: BackgroundTasks):
    """
    Run M/M/N queue simulation

    Parameters:
    - arrival_rate: λ (messages/sec)
    - num_threads: N (number of server threads)
    - service_rate: μ (messages/sec/thread)
    - sim_duration: Simulation time (seconds)
    - warmup_time: Warmup period to discard (seconds)
    - random_seed: Random seed for reproducibility
    """
    try:
        # Generate simulation ID
        sim_id = str(uuid.uuid4())

        # Create configuration
        config = MMNConfig(
            arrival_rate=request.arrival_rate,
            num_threads=request.num_threads,
            service_rate=request.service_rate,
            sim_duration=request.sim_duration,
            warmup_time=request.warmup_time,
            random_seed=request.random_seed,
            enable_qos=request.enable_qos
        )

        # Store simulation metadata
        simulation_service.create_simulation(
            sim_id=sim_id,
            model_type="M/M/N",
            config=config.dict(),
            status="running"
        )

        # Run simulation in background
        background_tasks.add_task(
            simulation_service.run_mmn_simulation,
            sim_id,
            config
        )

        return SimulationResponse(
            simulation_id=sim_id,
            status="running",
            model_type="M/M/N",
            message="Simulation started successfully",
            created_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mgn", response_model=SimulationResponse)
async def run_mgn(request: MGNSimulationRequest, background_tasks: BackgroundTasks):
    """
    Run M/G/N queue simulation with heavy-tailed distributions

    Parameters:
    - arrival_rate: λ (messages/sec)
    - num_threads: N (number of server threads)
    - service_rate: μ (mean messages/sec/thread)
    - distribution: Service time distribution (pareto, lognormal, exponential)
    - alpha: Pareto shape parameter (for heavy tails)
    - sim_duration: Simulation time (seconds)
    - warmup_time: Warmup period to discard (seconds)
    """
    try:
        sim_id = str(uuid.uuid4())

        config = MGNConfig(
            arrival_rate=request.arrival_rate,
            num_threads=request.num_threads,
            service_rate=request.service_rate,
            distribution=request.distribution,
            alpha=request.alpha,
            sim_duration=request.sim_duration,
            warmup_time=request.warmup_time,
            random_seed=request.random_seed,
            erlang_k=request.k,
            enable_qos=request.enable_qos
        )

        simulation_service.create_simulation(
            sim_id=sim_id,
            model_type="M/G/N",
            config=config.dict(),
            status="running"
        )

        background_tasks.add_task(
            simulation_service.run_mgn_simulation,
            sim_id,
            config
        )

        return SimulationResponse(
            simulation_id=sim_id,
            status="running",
            model_type="M/G/N",
            message="M/G/N simulation started successfully",
            created_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tandem", response_model=SimulationResponse)
async def run_tandem(request: TandemSimulationRequest, background_tasks: BackgroundTasks):
    """
    Run Tandem queue simulation (two-stage broker→receiver)

    Parameters:
    - arrival_rate: λ (messages/sec at broker)
    - n1, mu1: Stage 1 (broker) threads and service rate
    - n2, mu2: Stage 2 (receiver) threads and service rate
    - network_delay: Network propagation delay (seconds)
    - failure_prob: Transmission failure probability (0-1)
    """
    try:
        sim_id = str(uuid.uuid4())

        config = TandemQueueConfig(
            arrival_rate=request.arrival_rate,
            n1=request.n1,
            mu1=request.mu1,
            n2=request.n2,
            mu2=request.mu2,
            network_delay=request.network_delay,
            failure_prob=request.failure_prob,
            sim_duration=request.sim_duration,
            warmup_time=request.warmup_time,
            random_seed=request.random_seed
        )

        simulation_service.create_simulation(
            sim_id=sim_id,
            model_type="Tandem",
            config=config.dict(),
            status="running"
        )

        background_tasks.add_task(
            simulation_service.run_tandem_simulation,
            sim_id,
            config
        )

        return SimulationResponse(
            simulation_id=sim_id,
            status="running",
            model_type="Tandem",
            message="Tandem queue simulation started successfully",
            created_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heterogeneous", response_model=SimulationResponse)
async def run_heterogeneous(request: HeterogeneousSimulationRequest, background_tasks: BackgroundTasks):
    """
    Run Heterogeneous M/M/N simulation
    """
    try:
        sim_id = str(uuid.uuid4())

        config = HeterogeneousMMNConfig(
            arrival_rate=request.arrival_rate,
            server_groups=[ServerGroup(**g) for g in request.server_groups],
            selection_policy=request.selection_policy,
            sim_duration=request.sim_duration,
            warmup_time=request.warmup_time,
            random_seed=request.random_seed
        )

        simulation_service.create_simulation(
            sim_id=sim_id,
            model_type="Heterogeneous",
            config=config.dict(),
            status="running"
        )

        background_tasks.add_task(
            simulation_service.run_heterogeneous_simulation,
            sim_id,
            config
        )

        return SimulationResponse(
            simulation_id=sim_id,
            status="running",
            model_type="Heterogeneous",
            message="Heterogeneous simulation started successfully",
            created_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/distributed", response_model=SimulationResponse)
async def run_distributed(request: DistributedSimulationRequest, background_tasks: BackgroundTasks):
    """
    Run Distributed Broker simulation (Consistency/Ordering)
    """
    try:
        sim_id = str(uuid.uuid4())

        # Config dict for now since we don't have a DistributedConfig class exposed yet
        config = request.dict()

        simulation_service.create_simulation(
            sim_id=sim_id,
            model_type="Distributed",
            config=config,
            status="running"
        )

        background_tasks.add_task(
            simulation_service.run_distributed_simulation,
            sim_id,
            config
        )

        return SimulationResponse(
            simulation_id=sim_id,
            status="running",
            model_type="Distributed",
            message="Distributed simulation started successfully",
            created_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{simulation_id}/status", response_model=SimulationStatus)
async def get_simulation_status(simulation_id: str):
    """Get current status of a simulation"""
    simulation = simulation_service.get_simulation(simulation_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return SimulationStatus(
        simulation_id=simulation_id,
        status=simulation["status"],
        progress=simulation.get("progress", 0),
        message=simulation.get("message", ""),
        started_at=simulation["created_at"],
        completed_at=simulation.get("completed_at")
    )


@router.get("/{simulation_id}/results")
async def get_simulation_results(simulation_id: str):
    """Get results of a completed simulation"""
    simulation = simulation_service.get_simulation(simulation_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if simulation["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Simulation is {simulation['status']}, not completed"
        )

    return {
        "simulation_id": simulation_id,
        "model_type": simulation["model_type"],
        "config": simulation["config"],
        "results": simulation["results"],
        "metrics": simulation.get("metrics", {}),
        "completed_at": simulation.get("completed_at")
    }


@router.delete("/{simulation_id}")
async def delete_simulation(simulation_id: str):
    """Delete a simulation and its results"""
    success = simulation_service.delete_simulation(simulation_id)

    if not success:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return {"message": "Simulation deleted successfully", "simulation_id": simulation_id}


@router.websocket("/ws/{simulation_id}")
async def websocket_endpoint(websocket: WebSocket, simulation_id: str):
    """
    WebSocket endpoint for real-time simulation updates

    Sends periodic updates with:
    - Progress percentage
    - Current metrics (queue length, wait time, etc.)
    - Estimated time remaining
    """
    await websocket.accept()
    active_connections[simulation_id] = websocket

    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "simulation_id": simulation_id,
            "message": "WebSocket connected successfully"
        })

        # Keep connection alive and send updates
        while True:
            # Get current simulation status
            simulation = simulation_service.get_simulation(simulation_id)

            if simulation:
                # Send status update
                await websocket.send_json({
                    "type": "status",
                    "status": simulation["status"],
                    "progress": simulation.get("progress", 0),
                    "message": simulation.get("message", "")
                })

                # Send real-time metrics if available
                if "current_metrics" in simulation:
                    await websocket.send_json({
                        "type": "metrics",
                        "data": simulation["current_metrics"]
                    })

                # If completed, send final results
                if simulation["status"] == "completed":
                    await websocket.send_json({
                        "type": "completed",
                        "results": simulation.get("results", {})
                    })
                    break

                # If failed, send error
                if simulation["status"] == "failed":
                    await websocket.send_json({
                        "type": "error",
                        "message": simulation.get("error", "Simulation failed")
                    })
                    break

            # Wait before next update
            await asyncio.sleep(0.5)  # Update every 500ms

    except WebSocketDisconnect:
        if simulation_id in active_connections:
            del active_connections[simulation_id]
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        await websocket.close()
        if simulation_id in active_connections:
            del active_connections[simulation_id]


@router.get("/")
async def list_simulations():
    """List all simulations"""
    return simulation_service.list_simulations()
