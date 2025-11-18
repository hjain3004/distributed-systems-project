# Architecture Quick Reference Guide

**For developers navigating the frontend/backend stack**

---

## Visual Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (Port 4000)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ App.tsx (Main Component)                             │   │
│  │  ├─ Layout (Sidebar + Content)                       │   │
│  │  ├─ Routing (React Router)                           │   │
│  │  │  ├─ Dashboard                                     │   │
│  │  │  ├─ Simulate                                      │   │
│  │  │  ├─ Results                                       │   │
│  │  │  └─ Distributed                                  │   │
│  │  └─ Services                                         │   │
│  │     ├─ api.ts (HTTP calls)                           │   │
│  │     └─ websocket.ts (Real-time updates)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬──────────────────────────────────────┘
                      │ HTTP/WebSocket
                      │ (Axios + Socket.io)
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Port 6000)                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ main.py (FastAPI App)                               │   │
│  │  ├─ /api/simulations (M/M/N, M/G/N, Tandem)         │   │
│  │  ├─ /api/analytical (Erlang-C, M/G/N formulas)      │   │
│  │  ├─ /api/distributed (Raft, Vector Clocks, 2PC)    │   │
│  │  └─ /api/results (Export, Compare, Filter)          │   │
│  │                                                       │   │
│  │ Integration:                                         │   │
│  │  └─ src/ (Main simulation code)                      │   │
│  │     ├─ models/ (Queue simulations)                   │   │
│  │     └─ analysis/ (Analytical formulas)               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## File Location Map

### Frontend Components

```
frontend/src/
├── main.tsx                    # React DOM render
├── App.tsx                     # Main app layout
├── index.css                   # Global styles
├── components/
│   ├── Dashboard.tsx           # [TO BUILD] Summary page
│   ├── SimulationForm.tsx      # [TO BUILD] Config forms
│   ├── LiveMonitor.tsx         # [TO BUILD] Progress display
│   ├── ResultsChart.tsx        # [TO BUILD] Visualizations
│   └── ApiTest.tsx             # Demo component (working)
├── services/
│   ├── api.ts                  # HTTP client (429 lines, ready)
│   └── websocket.ts            # WebSocket client (ready)
├── types/
│   └── models.ts               # TypeScript types (231 lines, ready)
├── utils/
│   └── theme.ts                # Material-UI theme
└── pages/                      # [TO CREATE] React Router pages
    ├── DashboardPage.tsx
    ├── SimulatePage.tsx
    ├── ResultsPage.tsx
    └── DistributedPage.tsx
```

### Backend Routes

```
backend/api/
├── main.py                     # FastAPI initialization
├── routes/
│   ├── simulations.py          # M/M/N, M/G/N, Tandem endpoints
│   ├── analytical.py           # Erlang-C, M/G/N, Tandem formulas
│   ├── distributed.py          # Raft, Vector Clocks, 2PC
│   └── results.py              # Export, compare, filter
├── models/
│   ├── simulation_models.py    # Request/response Pydantic models
│   ├── analytical_models.py    # Analytical Pydantic models
│   └── distributed_models.py   # Distributed systems models
└── services/
    └── simulation_service.py   # Business logic & storage
```

---

## API Endpoints Summary

### Quick Lookup

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/simulations/mmn` | POST | Run M/M/N simulation |
| `/api/simulations/mgn` | POST | Run M/G/N (heavy-tailed) |
| `/api/simulations/tandem` | POST | Run tandem queue |
| `/api/simulations/{id}/status` | GET | Get simulation progress |
| `/api/simulations/{id}/results` | GET | Get completed results |
| `/api/simulations/ws/{id}` | WS | Real-time updates |
| `/api/analytical/mmn` | POST | Calculate M/M/N instantly |
| `/api/analytical/mgn` | POST | Calculate M/G/N instantly |
| `/api/analytical/tandem` | POST | Calculate tandem instantly |
| `/api/analytical/formulas` | GET | Get 15 formulas (LaTeX) |
| `/api/analytical/compare` | POST | Simulation vs analytical |
| `/api/distributed/raft` | POST | Raft consensus |
| `/api/distributed/vector-clocks` | POST | Vector clocks |
| `/api/distributed/two-phase-commit` | POST | 2PC |
| `/api/results/` | GET | List all results |
| `/api/results/{id}` | GET | Get result details |
| `/api/results/{id}/export` | GET | Export (json/csv) |
| `/api/docs` | GET | Swagger UI documentation |

---

## Type System Alignment

### How TypeScript ↔ Pydantic Sync Works

```
Backend (Python)                Frontend (TypeScript)
────────────────────────────────────────────────────────

class MMNConfig                interface MMNConfig
  arrival_rate: float      ←→    arrival_rate: number
  num_threads: int         ←→    num_threads: number
  service_rate: float      ←→    service_rate: number
  sim_duration: float      ←→    sim_duration: number
  warmup_time: float       ←→    warmup_time: number
  random_seed: int (opt)   ←→    random_seed?: number

class SimulationResponse        interface SimulationResponse
  simulation_id: str       ←→    simulation_id: string
  status: str              ←→    status: 'pending'|'running'|...
  model_type: str          ←→    model_type: QueueModelType
  message: str             ←→    message: string
  created_at: datetime     ←→    created_at: string
```

**Key Point:** TypeScript types in `frontend/src/types/models.ts` mirror Pydantic models in `backend/api/models/`.

---

## Common Development Tasks

### Add a New API Endpoint

**1. Backend: Add route handler**
```python
# backend/api/routes/simulations.py
@router.post("/my_new_endpoint")
async def my_handler(request: MyRequest):
    return MyResponse(...)
```

**2. Backend: Add Pydantic model**
```python
# backend/api/models/simulation_models.py
class MyRequest(BaseModel):
    param1: str
    param2: int

class MyResponse(BaseModel):
    result: str
```

**3. Frontend: Add TypeScript type**
```typescript
// frontend/src/types/models.ts
export interface MyRequest {
  param1: string;
  param2: number;
}
```

**4. Frontend: Add API call**
```typescript
// frontend/src/services/api.ts
export const myAPI = {
  callMyEndpoint: async (request: MyRequest): Promise<MyResponse> => {
    const response = await api.post<MyResponse>('/api/my_new_endpoint', request);
    return response.data;
  }
}
```

**5. Frontend: Use in component**
```typescript
// frontend/src/components/MyComponent.tsx
const result = await myAPI.callMyEndpoint({ param1: "test", param2: 42 });
```

---

### Add a New Component

**1. Create component file**
```typescript
// frontend/src/components/NewFeature.tsx
export const NewFeature = () => {
  return <div>New feature</div>;
};
```

**2. Import in App.tsx**
```typescript
import { NewFeature } from './components/NewFeature';

function App() {
  return <NewFeature />;
}
```

**3. Or add to routing (when React Router added)**
```typescript
const routes = [
  { path: '/', element: <Dashboard /> },
  { path: '/simulate', element: <SimulatePage /> },
];
```

---

### Add a Chart

**Option 1: Recharts (Easiest)**
```typescript
import { LineChart, Line, CartesianGrid, XAxis, YAxis } from 'recharts';

export const MyChart = ({ data }) => (
  <LineChart width={600} height={400} data={data}>
    <CartesianGrid />
    <XAxis dataKey="time" />
    <YAxis />
    <Line type="monotone" dataKey="value" stroke="#8884d8" />
  </LineChart>
);
```

**Option 2: ECharts (More features)**
```typescript
import EChartsReact from 'echarts-for-react';

const option = {
  xAxis: { type: 'category', data: ['A', 'B', 'C'] },
  yAxis: { type: 'value' },
  series: [{ data: [10, 20, 15], type: 'line' }]
};

export const MyChart = () => (
  <EChartsReact option={option} />
);
```

**Option 3: Visx (Most control)**
```typescript
import { BarGroup, Bar } from '@visx/shape';
import { scaleLinear, scaleBand } from '@visx/scale';

export const MyChart = ({ data }) => {
  const xScale = scaleBand({ ... });
  const yScale = scaleLinear({ ... });
  return (
    <svg width={600} height={400}>
      <BarGroup {...} />
    </svg>
  );
};
```

---

## Data Flow Examples

### Example 1: Running a Simulation

```
User clicks "Run M/M/N"
  ↓
Frontend form validation
  ↓
simulationAPI.runMMN({ arrival_rate: 100, ... })
  ↓
POST /api/simulations/mmn (Axios)
  ↓
Backend simulations.py route
  ↓
Creates MMNConfig from request
  ↓
Calls run_mmn_simulation(config)
  ↓
Stores in SimulationService with UUID
  ↓
Returns SimulationResponse (id, "running")
  ↓
Frontend shows simulation ID
  ↓
Frontend polls GET /api/simulations/{id}/status
  ↓
Backend returns { status: "running", progress: 45 }
  ↓
Frontend shows progress bar
  ↓
When done: GET /api/simulations/{id}/results
  ↓
Backend returns full SimulationResults with metrics
  ↓
Frontend displays charts and statistics
```

### Example 2: WebSocket Real-time Updates

```
GET /api/simulations/{id}/results pending
  ↓
Frontend connects to WS /api/simulations/ws/{id}
  ↓
Backend sends: { type: "connected", simulation_id: "..." }
  ↓
Every 500ms:
  Backend sends { type: "status", progress: 45, message: "..." }
  Frontend updates progress bar
  ↓
Backend sends { type: "metrics", data: { ... } }
  Frontend updates live charts
  ↓
When complete:
  Backend sends { type: "completed", results: { ... } }
  Frontend closes WebSocket, shows results
```

---

## Debugging Checklist

### Frontend Not Connecting to Backend?

- [ ] Is backend running? `ps aux | grep uvicorn`
- [ ] Is frontend running? Check http://localhost:4000
- [ ] Check CORS headers in DevTools Network tab
- [ ] Verify API_URL in `.env` matches backend port
- [ ] Check browser console for error messages

### TypeScript Errors?

- [ ] Run `npm run type-check` in frontend/
- [ ] Check that types match between frontend and backend
- [ ] Ensure Pydantic models are in `models.ts`
- [ ] Verify import paths use absolute paths

### API Endpoint Not Working?

- [ ] Check endpoint exists in `backend/api/routes/`
- [ ] Verify route is included in `main.py` with correct prefix
- [ ] Test directly: `curl http://localhost:6000/api/health`
- [ ] Check Swagger docs at http://localhost:6000/api/docs
- [ ] Look for import errors in backend console

### WebSocket Not Connecting?

- [ ] Check WebSocket URL in `.env`: `ws://localhost:6000`
- [ ] Verify backend has `@router.websocket()` endpoint
- [ ] Check browser console for WebSocket errors
- [ ] Test with simple echo server first

---

## Key Directories to Know

| Directory | Purpose | Examples |
|-----------|---------|----------|
| `frontend/src` | React component code | Components, services, types |
| `backend/api` | FastAPI endpoint code | Routes, models, services |
| `src/` | Main simulation code | Queue models, analysis |
| `experiments/` | Experimental scripts | Test data, validation |
| `visualization/` | Plot generation | Existing matplotlib plots |

---

## Performance Tips

### Frontend
- Use React.memo() for expensive components
- Use useCallback() for event handlers
- Lazy load routes with React.lazy()
- Virtualize long lists

### Backend
- Use async endpoints for I/O operations
- Cache analytical calculations
- Use background tasks for long simulations
- Add pagination to list endpoints

---

## Testing Strategy

### Frontend Tests (To Add)
```bash
npm run test              # Jest unit tests
npm run type-check       # TypeScript compilation
```

### Backend Tests (Existing)
```bash
pytest tests/            # Unit tests
./test_all.sh           # Full integration tests
```

### Manual Testing
```bash
# 1. Start backend
python backend/simple_main.py

# 2. Start frontend
cd frontend && npm run dev

# 3. Test health
curl http://localhost:6000/api/health

# 4. Open browser
http://localhost:4000
```

---

## Important Port Numbers

- **Frontend:** 4000 (Vite dev server)
- **Backend:** 6000 (FastAPI)
- **Docs:** 6000/api/docs (Swagger)
- **Do NOT use:** 3000, 5000, 8000 (common conflicts)

---

## Next Component Priority

### Phase 1 (Essential)
1. Dashboard layout
2. M/M/N simulation form
3. Simple results table

### Phase 2 (Important)
1. Recharts visualization
2. WebSocket integration
3. M/G/N and Tandem forms

### Phase 3 (Nice to have)
1. ECharts comparisons
2. Distributed systems UI
3. Export functionality

---

**Last Updated:** 2025-11-18  
**Status:** Production-ready infrastructure, components TBD
