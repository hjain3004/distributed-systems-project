# CLAUDE.md - AI Assistant Guide for Distributed Systems Project

> **Purpose**: This document provides comprehensive guidance for AI assistants (like Claude) working with this distributed systems performance modeling codebase.

**Last Updated**: 2025-11-15

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Architecture](#codebase-architecture)
3. [Key Design Patterns & Conventions](#key-design-patterns--conventions)
4. [Development Workflows](#development-workflows)
5. [Testing Strategy](#testing-strategy)
6. [Mathematical Foundation](#mathematical-foundation)
7. [Common Tasks Reference](#common-tasks-reference)
8. [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Project Overview

### What This Project Does

This is a **discrete-event simulation and analytical modeling framework** for cloud-based message broker performance analysis. It extends queueing theory research (Li et al. 2015) with:

- **Heavy-tailed workload modeling** using Pareto, lognormal, and Weibull distributions
- **Threading architecture analysis** (dedicated vs shared thread pools)
- **15 analytical equations** covering M/M/N, M/G/N, and threading models
- **Distributed systems protocols**: Raft consensus, Vector clocks, Two-Phase Commit
- **SimPy-based discrete-event simulation** for validation

### Core Research Question

**How do heavy-tailed service time distributions and threading architectures affect cloud message broker performance?**

### Technology Stack

```python
# Core Dependencies
simpy==4.1.1              # Discrete-event simulation engine
numpy==1.26.0             # Numerical computing
scipy==1.11.0             # Statistical distributions & special functions
pandas==2.1.0             # Data analysis
matplotlib==3.8.0         # Plotting
seaborn==0.13.0           # Statistical visualization
pydantic==2.5.0           # Type-safe configuration
pytest==7.4.0             # Unit testing
```

---

## Codebase Architecture

### Directory Structure

```
distributed-systems-project/
│
├── src/                          # Source code (DO NOT modify structure)
│   ├── core/                     # Core abstractions & utilities
│   │   ├── config.py            # Pydantic configuration classes
│   │   ├── distributions.py     # Service time distributions (Pareto, etc.)
│   │   └── metrics.py           # Performance metrics containers
│   │
│   ├── models/                   # Queue & protocol implementations
│   │   ├── base.py              # Abstract QueueModel base class
│   │   ├── mmn_queue.py         # M/M/N implementation
│   │   ├── mgn_queue.py         # M/G/N with heavy tails
│   │   ├── tandem_queue.py      # Two-stage broker→receiver model
│   │   ├── cloud_message.py     # Cloud message with visibility timeout
│   │   ├── visibility_timeout.py # Visibility timeout manager
│   │   ├── message_ordering.py  # In-order vs out-of-order delivery
│   │   ├── raft_consensus.py    # Raft leader election & log replication
│   │   ├── vector_clocks.py     # Causality tracking
│   │   ├── two_phase_commit.py  # 2PC atomic commit protocol
│   │   └── threading.py         # Threading model implementations
│   │
│   ├── analysis/                 # Analytical models & theory
│   │   ├── analytical.py        # All 15 equations (M/M/N, M/G/N, etc.)
│   │   ├── cap_analysis.py      # CAP theorem trade-offs
│   │   ├── extreme_value_theory.py  # EVT for tail latency
│   │   └── empirical_percentiles.py # Bootstrap confidence intervals
│   │
│   └── visualization/            # Plotting utilities
│       └── plot_config.py       # Consistent plot styling
│
├── experiments/                  # Experimental scripts
│   ├── run_basic_experiment.py  # M/M/N & M/G/N validation
│   ├── cloud_broker_simulation.py  # Visibility timeout experiments
│   ├── distributed_systems_validation.py  # Raft + Vector Clocks
│   ├── two_phase_commit_validation.py  # 2PC validation
│   ├── tandem_queue_validation.py  # Two-stage validation
│   └── paper_validation.py      # Compare with Li et al. (2015)
│
├── tests/                        # Unit tests
│   ├── test_erlang.py           # Erlang-C formula validation
│   ├── test_queueing_laws.py    # Little's Law, etc.
│   └── test_extreme_values.py   # EVT tests
│
├── debug/                        # Debugging & validation scripts
│   ├── validate_distributions.py  # Check Pareto, lognormal params
│   ├── validate_tandem_analytical.py  # Quick tandem validation
│   └── test_threading.py        # Threading model tests
│
├── visualization/                # Plot generation
│   └── generate_all_plots.py    # Generate all figures
│
├── README.md                     # User-facing documentation
├── TESTING_GUIDE.md             # How to run tests
├── requirements.txt             # Python dependencies
├── test_all.sh                  # Run all tests
└── rebuild_all.sh               # Rebuild & validate everything
```

### Key Architectural Principles

1. **Separation of Concerns**
   - `core/`: Generic abstractions (configs, distributions, metrics)
   - `models/`: Concrete queue and protocol implementations
   - `analysis/`: Mathematical formulas (analytical solutions)
   - `experiments/`: Runnable experiments (orchestrate models + analysis)

2. **Type Safety via Pydantic**
   - All configurations use Pydantic `BaseModel` with validation
   - Automatic stability checks (ρ < 1 for queues)
   - Computed properties for derived metrics

3. **SimPy Discrete-Event Simulation**
   - All queue models inherit from `QueueModel` abstract base
   - Use `simpy.Environment` for time progression
   - Use `simpy.Resource` for thread pools
   - Generator functions for message arrivals and processing

---

## Key Design Patterns & Conventions

### 1. Configuration Pattern (Pydantic)

**Convention**: Every model has a corresponding `*Config` class in `src/core/config.py`.

```python
# Example: M/M/N Configuration
from src.core.config import MMNConfig

config = MMNConfig(
    arrival_rate=100,      # λ (msg/sec)
    num_threads=10,        # N
    service_rate=12,       # μ (msg/sec/thread)
    sim_duration=1000,
    warmup_time=100,       # Discard first 100 sec
    random_seed=42
)

# Automatic validation
print(config.utilization)  # ρ = λ/(N·μ) = 0.833
```

**Important**:
- Pydantic validates `ρ < 1` (system stability) automatically
- Use `.utilization` property, not manual calculation
- Always set `random_seed` for reproducibility

### 2. Queue Model Pattern (Abstract Base Class)

**Convention**: All queue implementations extend `QueueModel` in `src/models/base.py`.

```python
from src.models.base import QueueModel
import simpy

class MyQueue(QueueModel):
    def model_name(self) -> str:
        return "M/Custom/N"

    def get_service_time(self) -> float:
        # Return service time sample
        return np.random.exponential(1.0 / self.config.service_rate)
```

**Key Methods**:
- `process_message(msg_id)`: Core queueing logic (arrival → wait → service → departure)
- `message_generator()`: Poisson arrival process
- `run()`: Execute simulation and return `SimulationMetrics`

### 3. Metrics Pattern (Dataclass)

**Convention**: Use `SimulationMetrics` from `src/core/metrics.py` for all simulation results.

```python
from src.core.metrics import SimulationMetrics

metrics = run_simulation(config)
stats = metrics.summary_statistics()

print(f"Mean wait: {stats['mean_wait']:.6f} sec")
print(f"P99 response: {stats['p99_response']:.6f} sec")

# Export to CSV
metrics.save("results.csv")
```

**Collected Data**:
- `wait_times`: Time in queue before service
- `service_times`: Service duration
- `response_times`: Wait + service
- `queue_lengths`: Queue depth at arrival
- Percentiles: P50, P95, P99

### 4. Analytical Model Pattern

**Convention**: Analytical formulas live in `src/analysis/analytical.py` with clear equation numbers.

```python
from src.analysis.analytical import MMNAnalytical

analytical = MMNAnalytical(
    arrival_rate=100,
    num_threads=10,
    service_rate=12
)

# All formulas return exact values (no simulation)
print(f"Erlang-C: {analytical.erlang_c():.6f}")  # Eq. 3
print(f"Mean Wq: {analytical.mean_waiting_time():.6f}")  # Eq. 5
```

**Classes**:
- `MMNAnalytical`: Equations 1-5 (M/M/N baseline)
- `MGNAnalytical`: Equations 6-10 (heavy-tailed extension)
- `TandemQueueAnalytical`: Two-stage model (Li et al. 2015)

### 5. Warmup Period Pattern

**Convention**: Always discard initial transient period.

```python
config = MMNConfig(
    sim_duration=1000,
    warmup_time=100,  # Discard first 100 sec
    ...
)
```

**Why**: Queues start empty. Initial measurements are biased until system reaches steady state.

### 6. Naming Conventions

| Concept | Variable Name | Example |
|---------|---------------|---------|
| Arrival rate | `arrival_rate` or `lambda_` | `λ = 100 msg/sec` |
| Service rate | `service_rate` or `mu` | `μ = 12 msg/sec/thread` |
| Number of threads | `num_threads` or `N` | `N = 10` |
| Utilization | `rho` or `utilization` | `ρ = λ/(N·μ)` |
| Traffic intensity | `a` or `traffic_intensity` | `a = λ/μ` |
| Pareto shape | `alpha` | `α = 2.5` |
| Pareto scale | `scale` or `k` | Auto-calculated to match mean |

**Critical**: In comments and docstrings, use Greek symbols (λ, μ, ρ) for readability.

---

## Development Workflows

### Workflow 1: Adding a New Queue Model

1. **Create configuration class** in `src/core/config.py`:
   ```python
   class MyQueueConfig(QueueConfig):
       model_type: Literal["MyQueue"] = "MyQueue"
       # Add model-specific parameters
   ```

2. **Implement queue model** in `src/models/my_queue.py`:
   ```python
   from src.models.base import QueueModel

   class MyQueue(QueueModel):
       def model_name(self) -> str:
           return "MyQueue"

       def get_service_time(self) -> float:
           # Return service time sample
           pass
   ```

3. **Create analytical model** in `src/analysis/analytical.py`:
   ```python
   class MyQueueAnalytical:
       def mean_waiting_time(self) -> float:
           # Return analytical Wq
           pass
   ```

4. **Add validation experiment** in `experiments/validate_my_queue.py`:
   ```python
   # Compare simulation vs analytical
   ```

5. **Add unit tests** in `tests/test_my_queue.py`:
   ```python
   def test_my_queue_stability():
       # Test ρ < 1 validation
       pass
   ```

### Workflow 2: Running Experiments

```bash
# 1. Basic validation (M/M/N, M/G/N)
python experiments/run_basic_experiment.py

# 2. Cloud broker features (visibility timeout, replication, ordering)
python experiments/cloud_broker_simulation.py

# 3. Distributed protocols (Raft, Vector Clocks)
python experiments/distributed_systems_validation.py

# 4. Two-Phase Commit
python experiments/two_phase_commit_validation.py

# 5. Tandem queue (two-stage broker→receiver)
python experiments/tandem_queue_validation.py

# 6. Paper validation (compare with Li et al. 2015)
python experiments/paper_validation.py

# 7. Run ALL tests
./test_all.sh
```

### Workflow 3: Debugging Distributions

```bash
# Validate Pareto distribution parameters
python debug/validate_distributions.py

# Check Pareto math (mean, variance, CV)
python debug/check_pareto_math.py

# Test threading models
python debug/test_threading.py

# Quick tandem queue validation
python debug/validate_tandem_analytical.py
```

### Workflow 4: Generating Plots

```bash
# Generate all figures
python visualization/generate_all_plots.py

# Individual plots
python visualization/plot_5_confidence_intervals.py
python experiments/analytic_vs_simulation_plots.py
```

---

## Testing Strategy

### Test Organization

1. **Unit Tests** (`tests/`)
   - `test_erlang.py`: Erlang-C formula validation
   - `test_queueing_laws.py`: Little's Law, utilization law
   - `test_extreme_values.py`: Extreme value theory tests

2. **Integration Tests** (`experiments/*_validation.py`)
   - Compare simulation vs analytical results
   - Validate distributed protocols (Raft, 2PC, etc.)

3. **Smoke Test** (`test_all.sh`)
   - Run all experiments quickly
   - Check for crashes and basic correctness

### Running Tests

```bash
# Unit tests
pytest tests/ -v

# Integration tests
python experiments/run_basic_experiment.py
python experiments/distributed_systems_validation.py

# All tests
./test_all.sh
```

### Expected Test Results

**Success Criteria**:
- Simulation vs analytical error < 10-15% (due to stochastic variation)
- Raft: Exactly 1 leader elected, all nodes agree
- Vector Clocks: Send-receive detected as "happened_before"
- 2PC: 100% commit rate when all vote YES
- Tandem: Stage 2 arrival rate Λ₂ = λ/(1-p) validated

---

## Mathematical Foundation

### The 15 Core Equations

**Section 1: M/M/N Baseline (Equations 1-5)**

```
1. Utilization:        ρ = λ/(N·μ)
2. P₀:                 Erlang-C formula (system empty probability)
3. Erlang-C:           C(N,a) = P(wait > 0)
4. Mean Queue Length:  Lq = C(N,a) · ρ/(1-ρ)
5. Mean Waiting Time:  Wq = Lq/λ (Little's Law)
```

**Section 2: Heavy-Tailed Extension (Equations 6-10)**

```
6. Pareto PDF:         f(t) = α·k^α / t^(α+1)
7. Mean:               E[S] = α·k/(α-1)
8. Second Moment:      E[S²] = α·k²/(α-2)
9. Coefficient of Variation: C² = 1/(α(α-2))  [CORRECTED]
10. M/G/N Waiting Time: Wq ≈ C(N,λ/μ)·(ρ/(1-ρ))·(E[S]/2)·(1+C²)
```

**Section 3: Threading Models (Equations 11-15)**

```
11. Dedicated Max Connections:  Nmax = Nthreads/2
12. Dedicated Throughput:       X = min(λ, (Nthreads/2)·μ)
13. Shared Overhead:            μeff = μ/(1 + α·Nactive/Nthreads)
14. Thread Saturation:          Psaturate = C(N,λ/μ)·ρ
15. P99 Latency:                R99 ≈ E[R] + 2.33·σR
```

### Tandem Queue Model (Li et al. 2015)

**Critical Insight**: Stage 2 sees HIGHER arrival rate due to retransmissions!

```
Stage 1 (Broker):      ρ₁ = λ/(n₁·μ₁)
Stage 2 (Receiver):    Λ₂ = λ/(1-p)  [p = failure probability]
                       ρ₂ = Λ₂/(n₂·μ₂) = λ/((1-p)·n₂·μ₂)

Network Time:          E[Network] = (2 + p)·D_link
Total Latency:         E[T] = W₁ + S₁ + (2+p)·D + W₂ + S₂
```

**Example**: With p=0.2 (20% failure rate), Stage 2 sees 25% more traffic!

### Distribution Formulas

**Pareto (Heavy-Tailed)**:
```python
# Scale parameter auto-calculated to match mean service time
scale = (1/μ) · (α-1)/α

# Coefficient of variation (corrected formula)
CV² = 1 / (α(α-2))
```

**Key Values**:
- α = 2.1: Very heavy tail (CV² = 10)
- α = 2.5: Moderate tail (CV² = 1.0)
- α = 3.0: Light tail (CV² = 0.33)

---

## Common Tasks Reference

### Task 1: Run a Basic M/M/N Simulation

```python
from src.core.config import MMNConfig
from src.models.mmn_queue import run_mmn_simulation

config = MMNConfig(
    arrival_rate=100,
    num_threads=10,
    service_rate=12,
    sim_duration=1000,
    warmup_time=100,
    random_seed=42
)

metrics = run_mmn_simulation(config)
stats = metrics.summary_statistics()

print(f"Mean wait: {stats['mean_wait']:.6f} sec")
print(f"P99 response: {stats['p99_response']:.6f} sec")
```

### Task 2: Compare Simulation vs Analytical

```python
from src.analysis.analytical import MMNAnalytical

# Analytical
analytical = MMNAnalytical(
    arrival_rate=config.arrival_rate,
    num_threads=config.num_threads,
    service_rate=config.service_rate
)

analytical_wq = analytical.mean_waiting_time()
simulated_wq = stats['mean_wait']

error = abs(analytical_wq - simulated_wq) / analytical_wq * 100
print(f"Error: {error:.2f}%")  # Should be < 15%
```

### Task 3: Test Heavy-Tailed Workload (M/G/N)

```python
from src.core.config import MGNConfig
from src.models.mgn_queue import run_mgn_simulation

config = MGNConfig(
    arrival_rate=100,
    num_threads=10,
    service_rate=12,
    distribution="pareto",
    alpha=2.5,  # Shape parameter
    sim_duration=1000,
    warmup_time=100,
    random_seed=42
)

print(f"CV²: {config.coefficient_of_variation:.2f}")
print(f"Scale k: {config.scale:.6f}")

metrics = run_mgn_simulation(config)
stats = metrics.summary_statistics()
```

### Task 4: Validate Tandem Queue

```python
from src.core.config import TandemQueueConfig
from src.models.tandem_queue import run_tandem_simulation
from src.analysis.analytical import TandemQueueAnalytical

config = TandemQueueConfig(
    arrival_rate=100,
    n1=10, mu1=12,        # Stage 1 (broker)
    n2=12, mu2=12,        # Stage 2 (receiver needs more capacity!)
    network_delay=0.01,   # 10ms
    failure_prob=0.2,     # 20% failures
    sim_duration=1000,
    warmup_time=100
)

print(f"Stage 1 utilization: {config.stage1_utilization:.3f}")
print(f"Stage 2 effective arrival: {config.stage2_effective_arrival:.1f} msg/sec")
print(f"Stage 2 utilization: {config.stage2_utilization:.3f}")

# Run simulation
results = run_tandem_simulation(config)

# Compare with analytical
analytical = TandemQueueAnalytical(
    lambda_arrival=100,
    n1=10, mu1=12,
    n2=12, mu2=12,
    network_delay=0.01,
    failure_prob=0.2
)
analytical.compare_stages()
```

### Task 5: Test Distributed Systems Protocols

```python
# Raft Consensus
from src.models.raft_consensus import RaftCluster
import simpy

env = simpy.Environment()
cluster = RaftCluster(env=env, num_nodes=5)
env.run(until=50)

leader = cluster.get_leader()
print(f"Leader: Node {leader.node_id if leader else 'None'}")

# Vector Clocks
from src.models.vector_clocks import CausalityTracker

tracker = CausalityTracker(num_processes=3)
vc1 = tracker.local_event(0)
vc2 = tracker.send_event(0)
vc3 = tracker.receive_event(1, vc2)

relationship = tracker.check_causality(0, 2)
print(f"Causality: {relationship}")  # 'happened_before'

# Two-Phase Commit
from src.models.two_phase_commit import TwoPhaseCommitCluster

env = simpy.Environment()
cluster = TwoPhaseCommitCluster(env=env, num_participants=5, vote_yes_prob=1.0)
env.run(until=100)

metrics = cluster.coordinator.get_metrics()
print(f"Commit rate: {metrics['commit_rate']:.1f}%")  # Should be 100%
```

---

## AI Assistant Guidelines

### When Working with This Codebase

1. **DO NOT Restructure**
   - The `src/` directory structure is deliberate
   - Do not move files between `core/`, `models/`, `analysis/`
   - Do not rename core modules

2. **Always Preserve Type Safety**
   - All new configurations must use Pydantic `BaseModel`
   - Add validation for stability (ρ < 1)
   - Use `@property` for computed values

3. **Follow Equation Numbering**
   - When adding formulas to `analytical.py`, document equation numbers
   - Reference equations in docstrings: `"""Equation 3: Erlang-C"""`

4. **Maintain Simulation Consistency**
   - Always use `warmup_time` to discard transients
   - Set `random_seed` for reproducible results
   - Use `SimulationMetrics` for all result collection

5. **Testing is Required**
   - Add unit tests for new analytical formulas
   - Add validation experiments for new queue models
   - Ensure `./test_all.sh` passes

6. **Documentation Standards**
   - Use Greek symbols in docstrings (λ, μ, ρ, α)
   - Provide examples in docstrings
   - Update this CLAUDE.md when adding major features

### Common Mistakes to Avoid

**Mistake 1**: Manually calculating utilization
```python
# WRONG
rho = lambda_val / (N * mu)

# CORRECT
rho = config.utilization  # Uses Pydantic property
```

**Mistake 2**: Forgetting warmup period
```python
# WRONG
config = MMNConfig(..., warmup_time=0)  # Biased results!

# CORRECT
config = MMNConfig(..., warmup_time=100)  # Discard transients
```

**Mistake 3**: Not setting random seed
```python
# WRONG (non-reproducible)
config = MMNConfig(..., random_seed=None)

# CORRECT
config = MMNConfig(..., random_seed=42)
```

**Mistake 4**: Using wrong Pareto CV formula
```python
# WRONG (old formula)
CV_squared = 1.0 / (alpha - 2)

# CORRECT (fixed formula)
CV_squared = 1.0 / (alpha * (alpha - 2))
```

**Mistake 5**: Ignoring Stage 2 load amplification in tandem queues
```python
# WRONG (assumes Λ₂ = λ)
rho2 = lambda_val / (n2 * mu2)

# CORRECT (accounts for retransmissions)
Lambda2 = lambda_val / (1 - failure_prob)
rho2 = Lambda2 / (n2 * mu2)
```

### When to Ask the User

1. **Major architectural changes**
   - Restructuring `src/` directory
   - Changing core abstractions (QueueModel, Config classes)
   - Modifying equation numbering

2. **Research decisions**
   - Choosing distribution types (Pareto vs lognormal vs Weibull)
   - Setting experiment parameters (λ, μ, N, α)
   - Interpreting unexpected results (large simulation error)

3. **Performance trade-offs**
   - Simulation duration (accuracy vs runtime)
   - Number of replications (confidence vs time)
   - Warmup period length

### Quick Reference: File Purposes

| File | Purpose | Modify? |
|------|---------|---------|
| `src/core/config.py` | Configuration classes | Yes (add new configs) |
| `src/core/distributions.py` | Service time distributions | Yes (add new dists) |
| `src/core/metrics.py` | Performance metrics | Rarely |
| `src/models/base.py` | Abstract queue model | No |
| `src/models/mmn_queue.py` | M/M/N implementation | Rarely |
| `src/models/mgn_queue.py` | M/G/N implementation | Rarely |
| `src/models/tandem_queue.py` | Two-stage model | Rarely |
| `src/analysis/analytical.py` | All 15 equations | Yes (add new formulas) |
| `experiments/*.py` | Runnable experiments | Yes (add new experiments) |
| `tests/*.py` | Unit tests | Yes (add tests) |
| `README.md` | User documentation | Yes (keep updated) |
| `TESTING_GUIDE.md` | Testing instructions | Yes (add new tests) |

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-15 | 1.0 | Initial CLAUDE.md creation |

---

## Additional Resources

- **Li et al. (2015)**: "Modeling Message Queueing Services with Reliability Guarantee in Cloud Computing Environment Using Colored Petri Nets"
- **Kleinrock (1975)**: *Queueing Systems, Volume 1: Theory*
- **SimPy Documentation**: https://simpy.readthedocs.io/
- **Pydantic Documentation**: https://docs.pydantic.dev/

---

**Questions?** Check `README.md` for user-facing documentation or `TESTING_GUIDE.md` for testing workflows.
