# FastAPI Backend

REST API for Distributed Systems Performance Modeling

## Quick Start

### Installation

```bash
cd backend

# Install dependencies (includes main project requirements)
pip install -r requirements-api.txt

# Also install main project requirements if not already installed
pip install -r ../requirements.txt
```

### Run the Server

```bash
# From the backend directory
python -m uvicorn api.main:app --reload --port 8000

# Or run directly
python api/main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/api/redoc
- **Health**: http://localhost:8000/api/health

## API Endpoints

### Simulations

#### Run M/M/N Simulation
```bash
POST /api/simulations/mmn
```

**Request:**
```json
{
  "arrival_rate": 100.0,
  "num_threads": 10,
  "service_rate": 12.0,
  "sim_duration": 1000.0,
  "warmup_time": 100.0,
  "random_seed": 42
}
```

**Response:**
```json
{
  "simulation_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "running",
  "model_type": "M/M/N",
  "message": "Simulation started successfully",
  "created_at": "2025-11-17T12:00:00"
}
```

#### Run M/G/N Simulation
```bash
POST /api/simulations/mgn
```

#### Run Tandem Queue Simulation
```bash
POST /api/simulations/tandem
```

#### Get Simulation Status
```bash
GET /api/simulations/{simulation_id}/status
```

#### Get Simulation Results
```bash
GET /api/simulations/{simulation_id}/results
```

#### WebSocket (Real-time Updates)
```bash
WS /api/simulations/ws/{simulation_id}
```

### Analytical Calculations

#### M/M/N Analytical
```bash
POST /api/analytical/mmn
```

#### M/G/N Analytical
```bash
POST /api/analytical/mgn
```

#### Tandem Analytical
```bash
POST /api/analytical/tandem
```

#### Get Formulas
```bash
GET /api/analytical/formulas
```

### Distributed Systems

#### Raft Consensus
```bash
POST /api/distributed/raft
```

#### Vector Clocks
```bash
POST /api/distributed/vector-clocks
```

#### Two-Phase Commit
```bash
POST /api/distributed/two-phase-commit
```

### Results Management

#### List Results
```bash
GET /api/results/?model_type=M/M/N&status=completed&limit=50
```

#### Get Result
```bash
GET /api/results/{simulation_id}
```

#### Export Result
```bash
GET /api/results/{simulation_id}/export?format=json
GET /api/results/{simulation_id}/export?format=csv
```

#### Compare Results
```bash
POST /api/results/compare
```

## WebSocket Protocol

Connect to `/api/simulations/ws/{simulation_id}` for real-time updates.

**Message Types:**

1. **Connected**
```json
{
  "type": "connected",
  "simulation_id": "...",
  "message": "WebSocket connected successfully"
}
```

2. **Status Update**
```json
{
  "type": "status",
  "status": "running",
  "progress": 45.5,
  "message": "Processing..."
}
```

3. **Metrics Update** (during simulation)
```json
{
  "type": "metrics",
  "data": {
    "current_queue_length": 5.2,
    "current_wait_time": 0.045,
    "messages_processed": 4500
  }
}
```

4. **Completed**
```json
{
  "type": "completed",
  "results": { ... }
}
```

5. **Error**
```json
{
  "type": "error",
  "message": "Simulation failed: ..."
}
```

## Architecture

```
backend/
├── api/
│   ├── main.py              # FastAPI application entry point
│   ├── routes/              # API route handlers
│   │   ├── simulations.py   # Simulation endpoints + WebSocket
│   │   ├── analytical.py    # Analytical calculation endpoints
│   │   ├── distributed.py   # Distributed systems protocols
│   │   └── results.py       # Results management
│   ├── models/              # Pydantic request/response models
│   │   ├── simulation_models.py
│   │   ├── analytical_models.py
│   │   └── distributed_models.py
│   └── services/            # Business logic
│       └── simulation_service.py
├── requirements-api.txt     # API-specific dependencies
└── README.md               # This file
```

## Development

### Interactive API Docs

FastAPI provides automatic interactive documentation:

1. **Swagger UI**: http://localhost:8000/api/docs
   - Try out API endpoints
   - See request/response schemas
   - Test authentication

2. **ReDoc**: http://localhost:8000/api/redoc
   - Beautiful API documentation
   - Better for reading

### Testing

```bash
# Run a quick test
curl http://localhost:8000/api/health

# Run M/M/N simulation
curl -X POST http://localhost:8000/api/simulations/mmn \
  -H "Content-Type: application/json" \
  -d '{
    "arrival_rate": 100.0,
    "num_threads": 10,
    "service_rate": 12.0,
    "sim_duration": 100.0,
    "warmup_time": 10.0
  }'

# Get analytical calculation (instant)
curl -X POST http://localhost:8000/api/analytical/mmn \
  -H "Content-Type: application/json" \
  -d '{
    "arrival_rate": 100.0,
    "num_threads": 10,
    "service_rate": 12.0
  }'
```

### CORS Configuration

CORS is configured for local development:
- React dev server: http://localhost:3000
- Vite dev server: http://localhost:5173

To add more origins, edit `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-frontend-url.com"],
    ...
)
```

## Production Deployment

### Using Uvicorn

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker (future)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-api.txt .
COPY ../requirements.txt ../
RUN pip install -r requirements-api.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Notes

- **In-Memory Storage**: Current implementation uses in-memory storage for simulations. For production, use a database (PostgreSQL, MongoDB, etc.)
- **Background Tasks**: Simulations run as FastAPI background tasks. For production, consider Celery + Redis for distributed task queue
- **WebSocket Scaling**: For production, use Redis pub/sub or similar for multi-server WebSocket support

## Troubleshooting

**Import errors:**
```bash
# Make sure you're running from the backend directory
cd backend
python -m uvicorn api.main:app --reload
```

**CORS errors:**
- Check that frontend URL is in allow_origins list
- Ensure credentials are enabled if needed

**Simulation not running:**
- Check logs for errors
- Verify Python path includes main project src/
- Ensure all dependencies are installed

## License

Academic project for educational purposes.
