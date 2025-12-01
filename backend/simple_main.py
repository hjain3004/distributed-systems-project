"""
Simplified FastAPI Backend - No external simulation imports
Just health check and basic endpoints for testing
"""

import sys
import os

# Add project root and backend directory to path
# Add project root and backend directory to path
current_file = os.path.abspath(__file__)
backend_dir = os.path.dirname(current_file)
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)
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

@app.post("/api/analytical/mgn")
async def calculate_mgn_analytical(config: dict):
    """Calculate M/G/N metrics analytically"""
    try:
        from src.analysis.analytical import MGNAnalytical

        arrival_rate = config.get("arrival_rate")
        num_threads = config.get("num_threads")
        mean_service = config.get("mean_service")
        variance_service = config.get("variance_service")

        if not all([arrival_rate, num_threads, mean_service, variance_service]):
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameters"}
            )

        analytical = MGNAnalytical(
            arrival_rate=arrival_rate,
            num_threads=num_threads,
            mean_service=mean_service,
            variance_service=variance_service
        )
        metrics = analytical.all_metrics()

        return JSONResponse(content={
            "model_type": "M/G/N",
            "config": config,
            "metrics": metrics,
            "formulas_used": ["Eq. 9: Coefficient of Variation C²", "Eq. 10: M/G/N waiting time approximation"]
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})

@app.post("/api/analytical/tandem")
async def calculate_tandem_analytical(config: dict):
    """Calculate Tandem Queue metrics analytically"""
    try:
        from src.analysis.analytical import TandemQueueAnalytical

        lambda_arrival = config.get("arrival_rate")
        n1 = config.get("n1")
        mu1 = config.get("mu1")
        n2 = config.get("n2")
        mu2 = config.get("mu2")
        network_delay = config.get("network_delay")
        failure_prob = config.get("failure_prob")
        consistency_mode = config.get("consistency_mode", "out_of_order")

        if not all([lambda_arrival, n1, mu1, n2, mu2, network_delay is not None, failure_prob is not None]):
             return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameters"}
            )

        analytical = TandemQueueAnalytical(
            lambda_arrival=lambda_arrival,
            n1=n1,
            mu1=mu1,
            n2=n2,
            mu2=mu2,
            network_delay=network_delay,
            failure_prob=failure_prob,
            consistency_mode=consistency_mode
        )

        metrics = {
            "stage1_waiting_time": analytical.stage1_waiting_time(),
            "stage1_utilization": config.get("arrival_rate") / (config.get("n1") * config.get("mu1")),
            "stage2_waiting_time": analytical.stage2_waiting_time(),
            "stage2_effective_arrival": config.get("arrival_rate") / (1 - config.get("failure_prob")),
            "stage2_utilization": (config.get("arrival_rate") / (1 - config.get("failure_prob"))) / (config.get("n2") * config.get("mu2")),
            "network_time": analytical.expected_network_time(),
            "total_latency": analytical.total_message_delivery_time(),
            "load_amplification": (config.get("arrival_rate") / (1 - config.get("failure_prob"))) / config.get("arrival_rate")
        }

        return JSONResponse(content={
            "model_type": "Tandem",
            "config": config,
            "metrics": metrics,
            "formulas_used": ["Stage 2 arrival: Λ₂ = λ/(1-p)", "Total latency: W₁ + S₁ + (2+p)·D + W₂ + S₂"]
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})

@app.post("/api/analytical/compare")
async def compare_simulation_vs_analytical(config: dict):
    """Compare simulation vs analytical"""
    # Mock comparison for demo purposes if real simulation is too slow
    return JSONResponse(content={
        "model_type": "M/M/N",
        "comparison": {
            "mean_waiting_time": {"simulation": 0.052, "analytical": 0.051, "error_percent": 1.9, "valid": True},
            "mean_queue_length": {"simulation": 1.55, "analytical": 1.53, "error_percent": 1.3, "valid": True}
        },
        "overall_valid": True
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3100)
