"""
FastAPI Backend with Full API Integration
Runs the complete analytical and simulation API
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
import uvicorn

# Import routes
from backend.api.routes import simulations, analytical, distributed, results

# Create FastAPI app
app = FastAPI(
    title="Distributed Systems Performance Modeling API",
    description="Backend API for queue modeling, analytical calculations, and distributed systems simulations",
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

# Include routers
app.include_router(simulations.router, prefix="/api/simulations", tags=["Simulations"])
app.include_router(analytical.router, prefix="/api/analytical", tags=["Analytical"])
app.include_router(distributed.router, prefix="/api/distributed", tags=["Distributed Systems"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "Distributed Systems Performance Modeling API",
        "version": "1.0.0",
        "message": "Full API with analytical endpoints active!"
    })

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(content={
        "message": "Distributed Systems Performance Modeling API",
        "docs": "/api/docs",
        "health": "/api/health",
        "version": "1.0.0",
        "endpoints": {
            "analytical": "/api/analytical",
            "simulations": "/api/simulations",
            "distributed": "/api/distributed",
            "results": "/api/results"
        }
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
