# Frontend Development Plan
**Distributed Systems Performance Modeling - Interactive Web Platform**

Last Updated: 2025-11-17

---

## ✅ Completed Work

### Phase 1: Research & Planning (COMPLETE)
- ✅ Comprehensive analysis of state-of-the-art visualization frameworks (2025)
- ✅ Technology stack selection and documentation (`FRONTEND_TECH_STACK.md`)
- ✅ Hybrid visualization approach: Visx + Recharts + ECharts + Plotly
- ✅ Architecture design and project structure planning

### Phase 2: Backend API (COMPLETE)
- ✅ FastAPI application with full REST API
- ✅ WebSocket support for real-time updates
- ✅ Complete route handlers:
  - `/api/simulations` - M/M/N, M/G/N, Tandem queue simulations
  - `/api/analytical` - Instant analytical calculations
  - `/api/distributed` - Raft, Vector Clocks, 2PC protocols
  - `/api/results` - Results management and export
- ✅ Pydantic models for type-safe validation
- ✅ Simulation service layer for background tasks
- ✅ Integration with existing Python modules
- ✅ Swagger/ReDoc automatic documentation
- ✅ CORS configuration for local development

### Phase 3: Frontend Foundation (COMPLETE)
- ✅ Vite + React 18 + TypeScript 5 setup
- ✅ Complete project structure:
  ```
  frontend/
  ├── src/
  │   ├── components/     # React components
  │   ├── pages/          # Page components
  │   ├── services/       # API & WebSocket services ✅
  │   ├── hooks/          # Custom React hooks
  │   ├── types/          # TypeScript definitions ✅
  │   └── utils/          # Utility functions
  ├── package.json ✅
  ├── tsconfig.json ✅
  └── vite.config.ts ✅
  ```
- ✅ TypeScript type definitions mirroring backend models
- ✅ Axios-based API service layer with interceptors
- ✅ WebSocket service with Socket.IO client
- ✅ Path aliases configured (@components, @services, etc.)
- ✅ Dependencies installed:
  - React + React Router
  - Material-UI (MUI) v5
  - Visx (all core modules)
  - D3.js
  - Recharts
  - ECharts for React
  - Plotly.js
  - Axios + TanStack Query
  - Socket.IO client
  - KaTeX for LaTeX rendering

---

## 📋 Next Steps: Component Development

### Phase 4: Core Components & Routing
**Estimated Time: 2-3 days**

#### 4.1 Main App Structure
Create the following core files:

```typescript
// src/main.tsx - Entry point
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

// src/App.tsx - Main application
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider, CssBaseline } from '@mui/material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { theme } from './utils/theme'

// Pages
import Dashboard from './pages/Dashboard'
import Configure from './pages/Configure'
import Simulate from './pages/Simulate'
import Analyze from './pages/Analyze'
import Distributed from './pages/Distributed'
import Results from './pages/Results'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/configure" element={<Configure />} />
            <Route path="/simulate" element={<Simulate />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/distributed" element={<Distributed />} />
            <Route path="/results" element={<Results />} />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
```

#### 4.2 Layout Components
- `<MainLayout />` - Navigation sidebar + header
- `<PageHeader />` - Page title and breadcrumbs
- `<LoadingSpinner />` - Loading states
- `<ErrorBoundary />` - Error handling

#### 4.3 Common Components
- `<MetricCard />` - Display single metric with icon
- `<ConfigPanel />` - Configuration forms wrapper
- `<ResultsTable />` - Data grid for results
- `<ExportButton />` - Export to CSV/JSON

---

### Phase 5: Configuration Forms
**Estimated Time: 2-3 days**

Build type-safe forms for each queue model:

```typescript
// src/components/configuration/MMNConfigForm.tsx
import { useForm } from 'react-hook-form'
import { TextField, Button, Grid } from '@mui/material'
import type { MMNConfig } from '@types/models'

export const MMNConfigForm = ({ onSubmit }: Props) => {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<MMNConfig>()

  // Real-time validation
  const arrivalRate = watch('arrival_rate')
  const numThreads = watch('num_threads')
  const serviceRate = watch('service_rate')
  const utilization = arrivalRate / (numThreads * serviceRate)

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <TextField
            label="Arrival Rate (λ)"
            type="number"
            {...register('arrival_rate', { required: true, min: 0.1 })}
            error={!!errors.arrival_rate}
            helperText="Messages per second"
          />
        </Grid>
        {/* ... more fields ... */}

        {/* Real-time utilization display */}
        <Alert severity={utilization >= 1 ? 'error' : 'success'}>
          ρ = {utilization.toFixed(3)} {utilization >= 1 && '(UNSTABLE!)'}
        </Alert>

        <Button type="submit" variant="contained">
          Run Simulation
        </Button>
      </Grid>
    </form>
  )
}
```

**Forms needed:**
- `MMNConfigForm` - M/M/N parameters
- `MGNConfigForm` - M/G/N with distribution selector
- `TandemConfigForm` - Two-stage parameters
- `RaftConfigForm` - Raft consensus
- `VectorClockForm` - Vector clocks
- `TwoPhaseCommitForm` - 2PC

---

### Phase 6: Visualization Components
**Estimated Time: 3-4 days**

#### 6.1 Visx Charts (Custom Scientific Visualizations)

```typescript
// src/components/visualization/QueueLengthChart.tsx
import { useMemo } from 'react'
import { Group } from '@visx/group'
import { LinePath, AreaClosed } from '@visx/shape'
import { scaleTime, scaleLinear } from '@visx/scale'
import { AxisBottom, AxisLeft } from '@visx/axis'
import { GridRows, GridColumns } from '@visx/grid'
import type { TimeSeriesDataPoint } from '@types/models'

export const QueueLengthChart = ({ data }: { data: TimeSeriesDataPoint[] }) => {
  const width = 800
  const height = 400
  const margin = { top: 20, right: 20, bottom: 40, left: 50 }

  const xScale = useMemo(() =>
    scaleTime({
      domain: [Math.min(...data.map(d => d.time)), Math.max(...data.map(d => d.time))],
      range: [margin.left, width - margin.right]
    }), [data]
  )

  const yScale = useMemo(() =>
    scaleLinear({
      domain: [0, Math.max(...data.map(d => d.value))],
      range: [height - margin.bottom, margin.top],
      nice: true
    }), [data]
  )

  return (
    <svg width={width} height={height}>
      <GridRows scale={yScale} width={width} height={height} stroke="#e0e0e0" />
      <GridColumns scale={xScale} width={width} height={height} stroke="#e0e0e0" />

      <LinePath
        data={data}
        x={d => xScale(d.time)}
        y={d => yScale(d.value)}
        stroke="#4CAF50"
        strokeWidth={2}
      />

      <AxisBottom top={height - margin.bottom} scale={xScale} label="Time (sec)" />
      <AxisLeft left={margin.left} scale={yScale} label="Queue Length" />
    </svg>
  )
}
```

**Charts to implement:**
- `QueueLengthChart` - Visx animated line chart
- `WaitTimeDistribution` - Visx histogram with Pareto overlay
- `AnalyticalComparison` - Visx dual-axis (sim vs analytical)
- `PercentileChart` - Recharts bar chart (P50/P95/P99)
- `DashboardSummary` - Recharts quick metrics
- `LiveQueueMonitor` - ECharts real-time streaming
- `ParameterHeatmap` - Plotly.js 2D heatmap
- `ParameterSpace3D` - Plotly.js 3D surface

#### 6.2 Distributed Systems Visualizations

```typescript
// src/components/visualization/RaftNetworkGraph.tsx
import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export const RaftNetworkGraph = ({ nodes, leader }: Props) => {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current) return

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink().distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(400, 300))

    // Render nodes with leader highlighted
    // Animate leader election

  }, [nodes, leader])

  return <svg ref={svgRef} width={800} height={600} />
}
```

---

### Phase 7: Real-Time Features
**Estimated Time: 2 days**

#### 7.1 WebSocket Integration

```typescript
// src/components/simulation/LiveSimulationMonitor.tsx
import { useEffect, useState } from 'react'
import { createSimulationWebSocket } from '@services/websocket'
import { LiveQueueMonitor } from '@components/visualization/LiveQueueMonitor'

export const LiveSimulationMonitor = ({ simulationId }: Props) => {
  const [metrics, setMetrics] = useState<MetricData[]>([])
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const ws = createSimulationWebSocket(simulationId)

    ws.onStatus((data) => {
      setProgress(data.progress)
    })

    ws.onMetrics((data) => {
      setMetrics(prev => [...prev, data])
    })

    ws.onCompleted((results) => {
      // Show final results
    })

    ws.connect()

    return () => ws.disconnect()
  }, [simulationId])

  return (
    <>
      <LinearProgress variant="determinate" value={progress} />
      <LiveQueueMonitor data={metrics} />
    </>
  )
}
```

#### 7.2 React Query Hooks

```typescript
// src/hooks/useSimulation.ts
import { useMutation, useQuery } from '@tanstack/react-query'
import { simulationAPI } from '@services/api'

export const useRunMMNSimulation = () => {
  return useMutation({
    mutationFn: simulationAPI.runMMN,
    onSuccess: (data) => {
      // Start WebSocket connection
    }
  })
}

export const useSimulationResults = (simulationId: string) => {
  return useQuery({
    queryKey: ['simulation', simulationId],
    queryFn: () => simulationAPI.getResults(simulationId),
    enabled: !!simulationId,
    refetchInterval: 2000, // Poll every 2 seconds
  })
}
```

---

### Phase 8: Page Components
**Estimated Time: 3 days**

#### 8.1 Dashboard Page
```typescript
// src/pages/Dashboard.tsx
- Recent experiments grid
- Quick-start cards (M/M/N, M/G/N, Tandem)
- Summary metrics from last run
- Performance charts
```

#### 8.2 Configure Page
```typescript
// src/pages/Configure.tsx
- Model type selector (tabs)
- Configuration form for selected model
- Real-time validation feedback
- Parameter presets dropdown
- Save/load configurations
```

#### 8.3 Simulate Page
```typescript
// src/pages/Simulate.tsx
- Active simulation display
- Live progress tracking
- Real-time metrics charts
- Pause/stop controls
- Results preview
```

#### 8.4 Analyze Page
```typescript
// src/pages/Analyze.tsx
- Analytical calculator
- Formula display with LaTeX
- Simulation vs analytical comparison
- Parameter sensitivity analysis
```

#### 8.5 Distributed Page
```typescript
// src/pages/Distributed.tsx
- Protocol selector
- Raft network visualization
- Vector clock timeline
- 2PC transaction viewer
```

#### 8.6 Results Page
```typescript
// src/pages/Results.tsx
- Results history table
- Filter and search
- Export buttons
- Delete functionality
- Comparison tool
```

---

## 🛠 Development Workflow

### Setup

```bash
# Backend
cd backend
pip install -r requirements-api.txt
pip install -r ../requirements.txt
python api/main.py  # Starts on http://localhost:8000

# Frontend
cd frontend
npm install
npm run dev  # Starts on http://localhost:3000
```

### Testing Flow

1. **Test API endpoints** - http://localhost:8000/api/docs
2. **Run a simulation** - POST to `/api/simulations/mmn`
3. **Connect WebSocket** - `/ws/simulations/{id}`
4. **Get results** - GET `/api/simulations/{id}/results`
5. **Verify in frontend** - Build UI components incrementally

---

## 📊 Implementation Priority

### Week 1: Core Infrastructure ✅ DONE
- ✅ Backend API structure
- ✅ Frontend project setup
- ✅ Type definitions
- ✅ API/WebSocket services

### Week 2: Basic UI (NEXT)
- Main layout and routing
- Dashboard page
- Configure page with M/M/N form
- Basic Visx chart

### Week 3: Simulations
- Simulation runner
- Real-time monitoring
- Results display
- All queue model forms

### Week 4: Visualizations
- All Visx charts
- Recharts integration
- ECharts streaming
- Distributed system visualizations

### Week 5: Advanced Features
- Plotly 3D charts
- Parameter exploration
- Results comparison
- Export functionality

### Week 6: Polish & Documentation
- Responsive design
- Error handling
- Loading states
- User documentation
- Deployment preparation

---

## 📁 Current Project Structure

```
distributed-systems-project/
├── backend/                      # ✅ COMPLETE
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   ├── routes/              # All endpoints
│   │   ├── models/              # Pydantic models
│   │   └── services/            # Business logic
│   ├── requirements-api.txt
│   └── README.md
│
├── frontend/                     # ✅ FOUNDATION COMPLETE
│   ├── src/
│   │   ├── components/          # 🔜 BUILD NEXT
│   │   ├── pages/               # 🔜 BUILD NEXT
│   │   ├── services/            # ✅ API & WebSocket
│   │   ├── hooks/               # 🔜 BUILD NEXT
│   │   ├── types/               # ✅ TypeScript defs
│   │   └── utils/               # 🔜 BUILD NEXT
│   ├── package.json             # ✅ All dependencies
│   ├── tsconfig.json            # ✅ Configured
│   ├── vite.config.ts           # ✅ Configured
│   └── index.html               # ✅ Entry point
│
├── src/                          # ✅ Existing Python modules
├── experiments/
├── tests/
├── FRONTEND_TECH_STACK.md        # ✅ Visualization analysis
├── FRONTEND_DEVELOPMENT_PLAN.md  # ✅ This file
└── README.md

```

---

## 🎯 Success Criteria

### Minimum Viable Product (MVP)
- [ ] Run M/M/N simulation from web UI
- [ ] Display results with Recharts
- [ ] Real-time progress tracking
- [ ] Analytical comparison
- [ ] Export results

### Full Feature Set
- [ ] All queue models (M/M/N, M/G/N, Tandem)
- [ ] All distributed protocols (Raft, Vector Clocks, 2PC)
- [ ] All visualization types (Visx, Recharts, ECharts, Plotly)
- [ ] Real-time WebSocket updates
- [ ] Parameter exploration
- [ ] Results history and comparison
- [ ] Export functionality
- [ ] Responsive design

---

## 🚀 Next Immediate Steps

**Start Here:**

1. **Create `src/main.tsx`** - React entry point
2. **Create `src/App.tsx`** - Main app with routing
3. **Create `src/utils/theme.ts`** - Material-UI theme
4. **Create `src/pages/Dashboard.tsx`** - Landing page
5. **Create `src/components/layout/MainLayout.tsx`** - Navigation
6. **Create `src/components/configuration/MMNConfigForm.tsx`** - First form
7. **Test with `npm run dev`**

---

## 📝 Notes

- **Backend is fully functional** - Can test all endpoints via Swagger UI
- **Frontend structure is ready** - All services and types defined
- **Next phase is component development** - Start with basic UI and forms
- **Incremental testing** - Build one feature at a time, test immediately
- **Visualization last** - Get data flowing first, then make it pretty

---

## 📚 References

- Backend API: http://localhost:8000/api/docs
- Visx Documentation: https://airbnb.io/visx/
- Material-UI: https://mui.com/
- React Query: https://tanstack.com/query/latest
- Vite: https://vitejs.dev/

---

**Status:** Backend complete, Frontend foundation ready, Ready for component development

**Last Updated:** 2025-11-17
