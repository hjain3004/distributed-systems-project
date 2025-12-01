# Frontend & Backend Architecture Summary
**Distributed Systems Performance Modeling Project**
**Date:** 2025-12-01

---

## Executive Summary

The project has a **fully structured full-stack application** with:
- ✅ **Frontend:** React 18 + TypeScript + Vite + Shadcn UI + Framer Motion (100% working)
- ✅ **Backend:** FastAPI with modular architecture (100% working)
- ✅ **API Client:** Type-safe Axios client with all endpoints defined
- ✅ **Type System:** Complete TypeScript/Pydantic alignment
- ✅ **Engineering Tools:** Capacity Planner, Blast Radius, Reality Gap Explorer implemented.

**Current Status:** Final Production Release.

---

## 1. FRONTEND ARCHITECTURE

### Framework & Technology Stack

```
Technology                Version      Purpose
─────────────────────────────────────────────────────────
React                     18.2.0       UI framework
React Router DOM          6.20.0       Client-side routing
TypeScript                5.3.3        Type safety
Vite                      5.0.8        Build tool + dev server
Shadcn UI                 Latest       Component library (Radix)
Tailwind CSS              3.x          Styling
Framer Motion             10.x         Animations
Recharts                  2.10.3       Data Visualization
Lucide React              Latest       Icons
```

### Key Frontend Components

**1. AppLayout.tsx**
- Sidebar navigation with Framer Motion animations.
- Responsive layout for all pages.

**2. ControlCenter.tsx ("The Storyteller")**
- Main demo page.
- **Simulation Engine**: Client-side approximation for real-time "Drama" (Pareto spikes, Legacy crashes).
- **Visuals**: Live time-series graphs, Topology view, "Oh Sh*t" button.

**3. MMNCalculator.tsx ("Capacity Planner")**
- **Inverse Solver**: Calculates required servers for target latency.
- **Utilization Curve**: Visualizes the "Hockey Stick" effect.

**4. TandemQueue.tsx ("The Blast Radius")**
- **Burst Propagation**: Visualizes how variance amplifies downstream.
- **Metrics**: Traffic Inflation and Inter-arrival Variance.

**5. MGNvsMMNComparison.tsx ("The Reality Gap Explorer")**
- **Multi-Line Chart**: Compares Theory (M/M/n) vs Approx (M/G/n) vs Reality (Sim).
- **Variance Slider**: Drives the divergence between the models.

---

## 2. BACKEND ARCHITECTURE

### Framework & Setup

```
Technology          Version      Purpose
─────────────────────────────────────────────
FastAPI             0.121.2      Web framework
Uvicorn             0.38.0       ASGI server
Pydantic            2.5.0        Data validation
SimPy               4.1.1        Discrete-event simulation
```

### API Endpoints

**Simulations**
```
POST   /api/simulations/mmn       - Run M/M/N simulation
POST   /api/simulations/mgn       - Run M/G/N simulation (heavy-tailed)
POST   /api/simulations/heterogeneous - Run Legacy/Heterogeneous sim
POST   /api/simulations/tandem    - Run tandem queue simulation
GET    /api/simulations/{id}/results
```

**Analytical**
```
POST   /api/analytical/mmn        - Calculate M/M/N metrics instantly
POST   /api/analytical/tandem     - Calculate tandem queue metrics
POST   /api/analytical/compare    - Compare simulation vs analytical
```

---

## 3. TECHNICAL DETAILS

### Port Configuration
- **Frontend Dev Server:** http://localhost:4000
- **Backend API:** http://localhost:3100
- **Swagger Docs:** http://localhost:3100/api/docs

### File Statistics

| Category | Count | Approx. Lines |
|----------|-------|---------------|
| Frontend Components | 15+ | 2000+ |
| Frontend Services | 2 | 500+ |
| Backend Routes | 4 | 500+ |
| Backend Models | 3 | 300+ |
| **Total** | **25+** | **~3,500** |

---

## CONCLUSION

**The full-stack infrastructure is complete.** The project has successfully transitioned from a "Calculator" to a set of "Engineering Tools" that support the "Scientific Proof" narrative.

✅ **Control Center**: Tuned for "Drama" (1.5s spikes, 36s crash).
✅ **Auxiliary Tools**: Fully upgraded for engineering analysis.
✅ **Architecture**: Robust, type-safe, and production-ready.

