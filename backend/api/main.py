"""
FastAPI Backend for Distributed Systems Performance Modeling
Main application entry point with CORS, WebSocket support, and routing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import routes
from .routes import simulations, analytical, distributed, results

# Create FastAPI app
app = FastAPI(
    title="Distributed Systems Performance Modeling API",
    description="Backend API for queue modeling, analytical calculations, and distributed systems simulations",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4000",  # Vite dev server
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
        "version": "1.0.0"
    })

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return JSONResponse(content={
        "message": "Distributed Systems Performance Modeling API",
        "docs": "/api/docs",
        "health": "/api/health",
        "version": "1.0.0"
    })

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=6000,
        reload=True,  # Auto-reload during development
        log_level="info"
    )
