"""
Simplified FastAPI Backend - No external simulation imports
Just health check and basic endpoints for testing
"""

import sys
import os

# Add project root and backend directory to path
sys.path.insert(0, '/home/user/distributed-systems-project')
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(
    title="Distributed Systems Performance Modeling API",
    description="Backend API for queue modeling (simplified version)",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4000",
        "http://127.0.0.1:4000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "Distributed Systems Performance Modeling API",
        "version": "1.0.0",
        "message": "Backend is running!"
    })

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(content={
        "message": "Distributed Systems Performance Modeling API",
        "docs": "/api/docs",
        "health": "/api/health",
        "version": "1.0.0"
    })

# Mock simulation endpoint for testing
@app.post("/api/simulations/mmn")
async def mock_mmn_simulation(config: dict):
    """Mock M/M/N simulation for testing frontend"""
    return JSONResponse(content={
        "simulation_id": "test-123",
        "status": "completed",
        "model_type": "M/M/N",
        "message": "Mock simulation (backend working!)",
        "metrics": {
            "mean_wait": 0.045,
            "mean_response": 0.128,
            "utilization": 0.833,
            "p99_response": 0.456
        }
    })

@app.post("/api/simulations/mgn")
async def mock_mgn_simulation(config: dict):
    """Mock M/G/N simulation for testing frontend"""
    distribution = config.get("distribution", "pareto")
    alpha = config.get("alpha", 2.5)

    return JSONResponse(content={
        "simulation_id": "test-mgn-456",
        "status": "completed",
        "model_type": "M/G/N",
        "message": f"Mock M/G/N simulation with {distribution} distribution (backend working!)",
        "config": {
            "distribution": distribution,
            "alpha": alpha
        },
        "metrics": {
            "mean_wait": 0.125,
            "mean_response": 0.208,
            "utilization": 0.833,
            "p99_response": 0.892,
            "coefficient_of_variation": 1.0
        }
    })

# Analytical endpoints
@app.post("/api/analytical/mmn")
async def calculate_mmn_analytical(config: dict):
    """Calculate M/M/N metrics analytically using real formulas"""
    try:
        from src.analysis.analytical import MMNAnalytical

        arrival_rate = config.get("arrival_rate")
        num_threads = config.get("num_threads")
        service_rate = config.get("service_rate")

        if not all([arrival_rate, num_threads, service_rate]):
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameters: arrival_rate, num_threads, service_rate"}
            )

        # Create analytical model
        analytical = MMNAnalytical(
            arrival_rate=arrival_rate,
            num_threads=num_threads,
            service_rate=service_rate
        )

        # Calculate all metrics
        metrics = analytical.all_metrics()

        return JSONResponse(content={
            "model_type": "M/M/N",
            "config": {
                "arrival_rate": arrival_rate,
                "num_threads": num_threads,
                "service_rate": service_rate
            },
            "metrics": metrics,
            "formulas_used": [
                "Eq. 1: Utilization ρ = λ/(N·μ)",
                "Eq. 2: Erlang-C formula",
                "Eq. 4: Mean queue length Lq",
                "Eq. 5: Mean waiting time Wq (Little's Law)"
            ]
        })

    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3100)
