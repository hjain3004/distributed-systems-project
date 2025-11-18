# Visualization & Frontend Component Roadmap

**A detailed guide for building the interactive UI for simulation results**

---

## Current State vs Target State

### Current State (Nov 18, 2025)
```
FRONTEND                           BACKEND
─────────────────────────────────────────────────────────
✅ React + TypeScript              ✅ FastAPI running
✅ Material-UI theme               ✅ All 20+ endpoints defined
✅ Vite dev server                 ✅ Pydantic models validated
✅ API client (429 lines)          ✅ WebSocket support
✅ Type definitions                ✅ Background task execution
✅ ApiTest component               ✅ Integration with Python code

⚠️ Only 1 working component        ⚠️ Minor uvicorn reload issue
❌ No routing                      ✅ (Workaround: simple_main.py)
❌ No forms
❌ No charts
❌ No data visualization
```

### Target State (After UI Development)
```
FRONTEND                           BACKEND
─────────────────────────────────────────────────────────
✅ Multi-page layout               ✅ Running actual simulations
✅ Configuration forms             ✅ Real-time metrics streaming
✅ Live progress monitoring        ✅ Instant analytical calculations
✅ Result visualizations           ✅ Distributed system simulations
✅ Comparative analysis             ✅ Export/comparison APIs
✅ Professional charts              ✅ Full type safety
✅ Mobile responsive                ✅ Performance optimized
```

---

## Phase-by-Phase Component Roadmap

### Phase 1: Core Navigation & Layout (2-3 hours)

**Goal:** Create professional multi-page structure

**Components to Build:**
1. **Layout.tsx** (Main wrapper)
   - Sidebar navigation
   - Header with title
   - Content area
   - Material-UI AppBar + Drawer

2. **Navigation.tsx**
   - Dashboard link
   - Simulate menu (M/M/N, M/G/N, Tandem)
   - Results link
   - Distributed Systems link

3. **Dashboard.tsx** (Home page)
   - Welcome message
   - Quick stats cards (using MUI Card)
   - Recent simulations table
   - Quick links to forms

**Implementation Hints:**
```typescript
import { AppBar, Drawer, List, ListItem, Card, CardContent } from '@mui/material';

// Summary card template
const StatCard = ({ title, value, unit }) => (
  <Card sx={{ mb: 2 }}>
    <CardContent>
      <Typography variant="overline">{title}</Typography>
      <Typography variant="h3">{value} {unit}</Typography>
    </CardContent>
  </Card>
);
```

---

### Phase 2: Simulation Configuration Forms (2-3 hours)

**Goal:** Allow users to configure and launch simulations

**Components to Build:**

1. **MMNForm.tsx**
   ```
   Fields: arrival_rate, num_threads, service_rate
          sim_duration, warmup_time, random_seed
   Features: Real-time validation, ρ < 1 check
             Min/max hints, help text
             Submit button
   ```

2. **MGNForm.tsx**
   ```
   Extends MMNForm with:
   - Distribution selector (dropdown)
   - Alpha parameter slider
   - CV² display
   - Pareto visualization preview
   ```

3. **TandemForm.tsx**
   ```
   Fields: arrival_rate, n1, mu1, n2, mu2
          network_delay, failure_prob
   Features: Stage indicators
             Load amplification calculation
             Network diagram preview
   ```

4. **SimulatePage.tsx**
   ```
   Container for forms
   Tabs: M/M/N | M/G/N | Tandem
   When submitted: Show LiveMonitor
   ```

**Implementation Hints:**
```typescript
import { TextField, Button, Select, Slider, FormControl, Alert } from '@mui/material';

const MMNForm = () => {
  const [config, setConfig] = useState<MMNConfig>({...});
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const handleValidation = () => {
    const rho = config.arrival_rate / (config.num_threads * config.service_rate);
    if (rho >= 1) {
      setErrors({ utilization: "Must be < 1 for stability" });
      return false;
    }
    return true;
  };
  
  const handleSubmit = async () => {
    if (handleValidation()) {
      const response = await simulationAPI.runMMN(config);
      // Navigate to live monitor with simulation_id
    }
  };
  
  return (
    <Box sx={{ p: 4 }}>
      <TextField 
        label="Arrival Rate (λ)"
        value={config.arrival_rate}
        onChange={e => setConfig({...config, arrival_rate: parseFloat(e.target.value)})}
        error={!!errors.arrival_rate}
        helperText={errors.arrival_rate}
      />
      {/* More fields... */}
      <Button variant="contained" onClick={handleSubmit}>Run Simulation</Button>
    </Box>
  );
};
```

---

### Phase 3: Live Simulation Monitoring (2-3 hours)

**Goal:** Show real-time progress and metrics during simulation

**Components to Build:**

1. **LiveMonitor.tsx**
   ```
   Displays:
   - Progress bar (0-100%)
   - Time elapsed / estimated remaining
   - Current metrics (queue length, wait time, messages processed)
   - Status messages
   
   Data source: WebSocket /api/simulations/ws/{id}
   Update frequency: Every 500ms
   ```

2. **ProgressCard.tsx**
   ```
   Shows:
   - Large progress percentage
   - Estimated completion time
   - Current status message
   Uses LinearProgress from MUI
   ```

3. **MetricsPanel.tsx**
   ```
   Live updating grid:
   - Current queue length
   - Current wait time
   - Messages processed
   - Processing rate (msgs/sec)
   Uses Grid from MUI
   ```

**Implementation Hints:**
```typescript
import { LinearProgress, Grid, Box, Typography } from '@mui/material';

const LiveMonitor = ({ simulationId }: { simulationId: string }) => {
  const [progress, setProgress] = useState(0);
  const [metrics, setMetrics] = useState<CurrentMetrics>({});
  const socketRef = useRef<Socket | null>(null);
  
  useEffect(() => {
    const socket = io(`ws://localhost:6000`, {
      path: `/api/simulations/ws/${simulationId}`
    });
    
    socket.on('status', (data) => {
      setProgress(data.progress);
    });
    
    socket.on('metrics', (data) => {
      setMetrics(data.data);
    });
    
    socketRef.current = socket;
    
    return () => socket.disconnect();
  }, [simulationId]);
  
  return (
    <Box sx={{ p: 4 }}>
      <LinearProgress variant="determinate" value={progress} />
      <Typography>{progress}%</Typography>
      
      <Grid container spacing={2} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6}>
          <MetricCard 
            label="Queue Length" 
            value={metrics.current_queue_length?.toFixed(2)} 
          />
        </Grid>
        {/* More metrics... */}
      </Grid>
    </Box>
  );
};
```

---

### Phase 4: Result Visualization (3-4 hours)

**Goal:** Display simulation results with interactive charts

**Components to Build:**

1. **ResultsPage.tsx** (Container)
   ```
   Tabs:
   - Metrics Summary (key numbers)
   - Distributions (histograms)
   - Percentiles (box plot)
   - Comparison (vs analytical)
   - Export (JSON/CSV)
   ```

2. **MetricsChart.tsx** (Recharts)
   ```
   Bar chart showing:
   - Mean wait time
   - Mean response time
   - Mean queue length
   - P50, P95, P99 values
   
   With legend and tooltips
   ```

3. **WaitTimeDistribution.tsx** (Visx)
   ```
   Histogram of all wait times
   - X-axis: wait time (seconds)
   - Y-axis: frequency
   - Overlay normal distribution
   ```

4. **AnalyticalComparison.tsx** (ECharts)
   ```
   Side-by-side comparison:
   - Simulation results
   - Analytical predictions
   - Error percentage
   
   Heatmap or table format
   ```

**Implementation Hints:**
```typescript
// Recharts example
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const ResultsChart = ({ metrics }: { metrics: SimulationMetrics }) => {
  const data = [
    { name: 'Mean Wait', value: metrics.mean_wait },
    { name: 'P95 Wait', value: metrics.p95_wait },
    { name: 'P99 Wait', value: metrics.p99_wait },
  ];
  
  return (
    <BarChart width={600} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis label={{ value: 'Time (sec)', angle: -90, position: 'insideLeft' }} />
      <Tooltip />
      <Legend />
      <Bar dataKey="value" fill="#8884d8" />
    </BarChart>
  );
};

// Visx example
import { HistogramBin, Histogram } from '@visx/shape';
import { scaleLinear } from '@visx/scale';

const WaitTimeDistribution = ({ waitTimes }: { waitTimes: number[] }) => {
  const xScale = scaleLinear({
    domain: [0, Math.max(...waitTimes)],
    range: [0, 600],
  });
  
  const yScale = scaleLinear({
    domain: [0, 100],
    range: [400, 0],
  });
  
  return (
    <svg width={700} height={450}>
      <Histogram
        data={waitTimes}
        xScale={xScale}
        yScale={yScale}
        bins={30}
      >
        {(bins) => (
          <g>
            {bins.map((bin, i) => (
              <HistogramBin
                key={i}
                bin={bin}
                x={() => xScale(bin.x0)}
                y={() => yScale(bin.length)}
                width={xScale(bin.x1) - xScale(bin.x0)}
                height={yScale(0) - yScale(bin.length)}
                fill="#66c2a5"
              />
            ))}
          </g>
        )}
      </Histogram>
    </svg>
  );
};
```

---

### Phase 5: Comparative Analysis (2-3 hours)

**Goal:** Compare multiple simulations and analytical results

**Components to Build:**

1. **ComparisonPage.tsx**
   ```
   Features:
   - Select multiple simulations
   - Load analytical results
   - Side-by-side comparison
   - Error metrics
   - Export comparison
   ```

2. **SimulationSelector.tsx**
   ```
   Multi-select dropdown
   Shows: Model type, config, completion time
   Filters by: Model type, date, status
   ```

3. **ComparisonTable.tsx**
   ```
   Table columns:
   - Metric name
   - Simulation 1 value
   - Simulation 2 value
   - Analytical value
   - Error %
   
   Color-coded: Green (< 10% error), Yellow (< 15%), Red (> 15%)
   ```

4. **LoadSensitivityChart.tsx** (ECharts)
   ```
   Shows impact of arrival_rate on metrics
   - X-axis: arrival_rate
   - Y-axis: mean_wait_time
   - Multiple lines for different thread counts
   ```

---

### Phase 6: Distributed Systems Visualization (2-3 hours)

**Goal:** Visualize Raft, Vector Clocks, and 2PC

**Components to Build:**

1. **RaftTopology.tsx**
   ```
   Diagram showing:
   - 5 nodes arranged in circle
   - Leader highlighted in red
   - Followers in blue
   - Log replication arrows
   - Current term displayed
   ```

2. **VectorClockTimeline.tsx**
   ```
   Timeline showing:
   - Processes on Y-axis
   - Time on X-axis
   - Events as dots
   - Causality relationships as arrows
   - "Happened before" relationships highlighted
   ```

3. **TwoPhaseCommitFlow.tsx**
   ```
   State diagram showing:
   - Coordinator at top
   - Participants below
   - Message flow
   - Commit/Abort decision
   - Transaction state
   ```

**Implementation Hints:**
```typescript
// Simple diagram with react-flow-renderer or custom SVG
import { Group } from '@visx/group';
import { Circle } from '@visx/shape';

const RaftTopology = ({ leader, followers }: RaftResults) => {
  const centerX = 300, centerY = 300, radius = 150;
  const nodes = [leader, ...followers];
  
  return (
    <svg width={600} height={600}>
      <Group left={centerX} top={centerY}>
        {nodes.map((node, i) => {
          const angle = (i / nodes.length) * 2 * Math.PI;
          const x = radius * Math.cos(angle);
          const y = radius * Math.sin(angle);
          
          return (
            <Group key={node.id} left={x} top={y}>
              <Circle
                r={40}
                fill={node.id === leader.id ? '#ff6b6b' : '#4c6ef5'}
              />
              <text textAnchor="middle" dominantBaseline="middle">
                Node {node.id}
              </text>
            </Group>
          );
        })}
      </Group>
    </svg>
  );
};
```

---

## Priority Implementation Order

### Tier 1: MVP (Must Have)
1. ✅ Navigation Layout
2. ✅ Dashboard page
3. ✅ M/M/N simulation form
4. ✅ Live progress monitor
5. ✅ Simple results display

**Time:** 4-6 hours
**Value:** Users can run simulations and see results

### Tier 2: Core Features
6. M/G/N form
7. Tandem form
8. Result charts (Recharts)
9. Analytical comparison
10. Export functionality

**Time:** 6-8 hours
**Value:** Full simulation capability + visualizations

### Tier 3: Advanced Features
11. Comparative analysis
12. Load sensitivity curves
13. Distributed systems UI
14. Dark mode
15. Mobile optimization

**Time:** 6-8 hours
**Value:** Professional, feature-complete application

---

## Data Integration Points

### Real Data vs Mock Data

**Current (Mock Data):**
```typescript
// ApiTest.tsx uses hardcoded values
const mockResult = {
  simulation_id: "test-123",
  status: "completed",
  model_type: "M/M/N",
  metrics: {
    mean_wait: 0.045,
    p99_response: 0.456,
    utilization: 0.833
  }
};
```

**Target (Real Data):**
```typescript
// Charts will use actual simulation results
const result = await simulationAPI.getResults(simulationId);
const metrics = result.metrics; // From backend

// Analytical comparison
const analytical = await analyticalAPI.calculateMMN({
  arrival_rate: result.config.arrival_rate,
  num_threads: result.config.num_threads,
  service_rate: result.config.service_rate
});

// Display comparison
<ComparisonChart 
  simulated={metrics}
  analytical={analytical.metrics}
/>
```

---

## Component Dependency Graph

```
App.tsx
├── Layout.tsx
│   ├── Header.tsx
│   └── Sidebar.tsx
│       ├── Dashboard (Page)
│       │   ├── StatCard.tsx (x4)
│       │   ├── RecentTable.tsx
│       │   └── QuickLinks.tsx
│       │
│       ├── Simulate (Page)
│       │   ├── TabContainer.tsx
│       │   ├── MMNForm.tsx
│       │   ├── MGNForm.tsx
│       │   ├── TandemForm.tsx
│       │   └── LiveMonitor.tsx
│       │       ├── ProgressCard.tsx
│       │       └── MetricsPanel.tsx
│       │
│       ├── Results (Page)
│       │   ├── ResultsTable.tsx
│       │   ├── MetricsChart.tsx
│       │   ├── WaitTimeDistribution.tsx
│       │   ├── AnalyticalComparison.tsx
│       │   └── ExportButton.tsx
│       │
│       ├── Compare (Page)
│       │   ├── SimulationSelector.tsx
│       │   ├── ComparisonTable.tsx
│       │   ├── LoadSensitivityChart.tsx
│       │   └── DownloadComparison.tsx
│       │
│       └── Distributed (Page)
│           ├── RaftTopology.tsx
│           ├── VectorClockTimeline.tsx
│           └── TwoPhaseCommitFlow.tsx
│
├── services/api.ts (Shared)
├── services/websocket.ts (Shared)
└── types/models.ts (Shared)
```

---

## Styling Strategy

### Material-UI Custom Theme

```typescript
// frontend/src/utils/theme.ts
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    success: { main: '#4caf50' },
    warning: { main: '#ff9800' },
    error: { main: '#f44336' },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2.5rem' },
    h2: { fontSize: '2rem' },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }
      }
    }
  }
});
```

### Responsive Design
- Mobile: 1 column layout
- Tablet: 2 column layout
- Desktop: 3+ column layout

Use MUI's Grid system:
```typescript
<Grid container spacing={2}>
  <Grid item xs={12} sm={6} md={4}>
    {/* Card on mobile (full width), tablet (half), desktop (third) */}
  </Grid>
</Grid>
```

---

## Testing Strategy for Components

### Unit Tests (with Jest + React Testing Library)
```typescript
describe('LiveMonitor', () => {
  it('displays progress bar', () => {
    render(<LiveMonitor simulationId="123" />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
  
  it('updates metrics when socket receives data', async () => {
    // Mock socket.io connection
    // Send mock metrics
    // Assert component updates
  });
});
```

### Integration Tests
- Form submission → API call → Result display
- WebSocket connection → Live updates
- Navigation → Page rendering

### Visual Tests
- Component rendering at different screen sizes
- Theme consistency
- Chart responsiveness

---

## Performance Optimization Tips

1. **Lazy Load Pages**
   ```typescript
   const Dashboard = React.lazy(() => import('./pages/Dashboard'));
   <Suspense fallback={<Loading />}>
     <Dashboard />
   </Suspense>
   ```

2. **Memoize Expensive Components**
   ```typescript
   export const ResultsChart = React.memo(({ data }) => {
     return <BarChart data={data} />;
   });
   ```

3. **Virtualize Long Lists**
   ```typescript
   import { FixedSizeList } from 'react-window';
   ```

4. **WebSocket Debouncing**
   ```typescript
   const debouncedMetricsUpdate = debounce(setMetrics, 500);
   socket.on('metrics', debouncedMetricsUpdate);
   ```

---

## Deployment Checklist

- [ ] All TypeScript errors resolved
- [ ] All console warnings fixed
- [ ] Built production bundle
- [ ] Environment variables set correctly
- [ ] API endpoints match production backend
- [ ] WebSocket URLs correct
- [ ] Charts responsive on mobile
- [ ] Forms validated
- [ ] Error messages user-friendly
- [ ] Loading states implemented
- [ ] Accessibility (ARIA labels, keyboard navigation)

---

## Summary

**This roadmap provides:**
- Clear phase breakdown (5 phases over 3-4 days)
- Specific components to build
- Code templates and patterns
- Data flow diagrams
- Testing strategy
- Performance tips

**Next Action:** Start Phase 1 by creating Layout.tsx and Navigation structure.

**Estimated Completion:** 15-20 hours of focused development

---

**Last Updated:** 2025-11-18
**Status:** Ready for implementation
