"""
Results Routes
Endpoints for managing simulation results (list, get, export, delete)
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List
import json
import csv
import io
from datetime import datetime
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from api.services.simulation_service import SimulationService

router = APIRouter()
simulation_service = SimulationService()


@router.get("/")
async def list_results(
    model_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """
    List all simulation results with optional filtering

    Query parameters:
    - model_type: Filter by model type (M/M/N, M/G/N, Tandem, etc.)
    - status: Filter by status (running, completed, failed)
    - limit: Maximum number of results (default 50)
    """
    try:
        simulations = simulation_service.list_simulations()

        # Apply filters
        if model_type:
            simulations = [s for s in simulations if s.get("model_type") == model_type]

        if status:
            simulations = [s for s in simulations if s.get("status") == status]

        # Limit results
        simulations = simulations[:limit]

        return {
            "total": len(simulations),
            "simulations": simulations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{simulation_id}")
async def get_result(simulation_id: str):
    """Get detailed results for a specific simulation"""
    simulation = simulation_service.get_simulation(simulation_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return simulation


@router.get("/{simulation_id}/export")
async def export_result(
    simulation_id: str,
    format: str = "json"
):
    """
    Export simulation results in various formats

    Supported formats:
    - json: JSON format
    - csv: CSV format (metrics only)
    """
    simulation = simulation_service.get_simulation(simulation_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if simulation["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot export {simulation['status']} simulation"
        )

    if format == "json":
        # Export as JSON
        json_str = json.dumps(simulation, indent=2, default=str)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=simulation_{simulation_id}.json"
            }
        )

    elif format == "csv":
        # Export metrics as CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Metric", "Value"])

        # Write metrics
        metrics = simulation.get("metrics", {})
        for key, value in metrics.items():
            writer.writerow([key, value])

        csv_content = output.getvalue()
        output.close()

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=simulation_{simulation_id}.csv"
            }
        )

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@router.delete("/{simulation_id}")
async def delete_result(simulation_id: str):
    """Delete a simulation and its results"""
    success = simulation_service.delete_simulation(simulation_id)

    if not success:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return {
        "message": "Simulation deleted successfully",
        "simulation_id": simulation_id
    }


@router.post("/compare")
async def compare_results(simulation_ids: List[str]):
    """
    Compare multiple simulation results side-by-side

    Useful for comparing different configurations or models
    """
    try:
        comparisons = []

        for sim_id in simulation_ids:
            simulation = simulation_service.get_simulation(sim_id)
            if simulation and simulation["status"] == "completed":
                comparisons.append({
                    "simulation_id": sim_id,
                    "model_type": simulation["model_type"],
                    "config": simulation["config"],
                    "metrics": simulation.get("metrics", {})
                })

        if not comparisons:
            raise HTTPException(status_code=400, detail="No valid simulations found for comparison")

        return {
            "total_compared": len(comparisons),
            "comparisons": comparisons
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
