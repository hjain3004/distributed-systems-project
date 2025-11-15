# Performance Modeling of Cloud Message Brokers

**Heavy-Tailed Workloads, Threading Models, and Distributed Systems Protocols**

This project extends queueing theory research to model cloud-based message broker performance with:
- Heavy-tailed service time distributions (M/G/N, M/Ek/N models)
- Explicit threading architecture modeling (dedicated vs shared)
- 15 derived performance equations with rigorous validation
- Distributed systems protocols (Raft, Vector Clocks, Two-Phase Commit)
- Discrete-event simulation using SimPy with statistical rigor (20+ replications)

## Project Overview

Based on research by Li et al. (2015) on cloud message queueing services, this project provides:
1. **Heavy-tailed distributions**: Pareto (with Erlang for reduced variance)
2. **Threading models**: Dedicated (thread-per-connection) vs Shared (worker pool)
3. **Analytical framework**: 15 equations covering M/M/N, M/G/N, M/Ek/N, and threading models
4. **Distributed protocols**: Raft consensus, Vector clocks, Two-Phase Commit (2PC)
5. **Cloud broker features**: Visibility timeout, replication, message ordering
6. **Comprehensive validation**: 29 unit tests, multiple experiments, analytical comparisons

## Quick Start

### Installation

```bash
# Clone or navigate to project directory
cd distributed-systems-project

# Install dependencies (no virtual environment needed for quick testing)
pip3 install simpy numpy scipy pandas matplotlib seaborn pydantic pytest

# Or use requirements.txt
pip3 install -r requirements.txt
```

### Run All Tests

```bash
# Quick test - run all distributed systems tests
./test_all.sh

# Comprehensive test - run unit tests
python3 -m pytest tests/ -v

# Output: 29 tests PASSED in ~97 seconds
```

### Run Basic Experiments

```bash
# M/M/N and M/G/N validation
python3 experiments/run_basic_experiment.py

# Cloud broker features (visibility timeout, replication, ordering)
python3 experiments/cloud_broker_simulation.py

# Distributed systems protocols (Raft, Vector Clocks, 2PC)
python3 experiments/distributed_systems_validation.py

# Tandem queue (two-stage broker→receiver)
python3 experiments/tandem_queue_validation.py
```

### Expected Output

```
======================================================================
 MESSAGE BROKER PERFORMANCE MODELING
 Basic Validation Experiments
======================================================================

======================================================================
EXPERIMENT 1: M/M/N Baseline Validation
======================================================================

Configuration:
  λ = 100 messages/sec
  N = 10 threads
  μ = 12 messages/sec/thread
  ρ = 0.833

Running simulation...
Simulation complete:
  Model: M/M/10
  Total messages: ...

Results Comparison:
Metric                         Analytical      Simulation        Error %
-----------------------------------------------------------------------------
Mean Waiting Time (sec)          ...             ...             < 10%
Mean Queue Length                ...             ...             < 15%
Mean Response Time (sec)         ...             ...             < 10%

======================================================================
EXPERIMENT 2: Heavy-Tailed Service Times (M/G/N)
======================================================================
...
```

## Project Structure

```
distributed-systems-project/
├── README.md                    # This file
├── CLAUDE.md                    # AI assistant guide
├── MATHEMATICAL_GUIDE.md        # Detailed mathematical explanations
├── TESTING_GUIDE.md             # Testing documentation
├── requirements.txt             # Python dependencies
├── test_all.sh                  # Run all tests
├── rebuild_all.sh               # Complete rebuild script
│
├── src/                         # Source code
│   ├── core/                    # Core abstractions
│   │   ├── config.py           # Pydantic configuration classes
│   │   ├── distributions.py    # Service time distributions
│   │   └── metrics.py          # Performance metrics
│   ├── models/                  # Queue & protocol implementations
│   │   ├── base.py             # Abstract base queue model
│   │   ├── mmn_queue.py        # M/M/N implementation
│   │   ├── mgn_queue.py        # M/G/N (heavy-tail) implementation
│   │   ├── mekn_queue.py       # M/Ek/N (Erlang) implementation
│   │   ├── tandem_queue.py     # Two-stage broker→receiver
│   │   ├── threading.py        # Threading model implementations
│   │   ├── raft_consensus.py   # Raft leader election
│   │   ├── vector_clocks.py    # Causality tracking
│   │   ├── two_phase_commit.py # 2PC protocol
│   │   ├── visibility_timeout.py # ACK/NACK mechanism
│   │   ├── distributed_broker.py # Replication
│   │   └── message_ordering.py # In-order vs out-of-order
│   ├── analysis/               # Analytical models
│   │   ├── analytical.py       # All 15 equations
│   │   ├── cap_analysis.py     # CAP theorem analysis
│   │   ├── extreme_value_theory.py # EVT for tail latency
│   │   └── empirical_percentiles.py # Bootstrap CI
│   └── visualization/          # Plotting utilities
│
├── experiments/                # Experimental scripts
│   ├── run_basic_experiment.py # M/M/N & M/G/N validation
│   ├── cloud_broker_simulation.py # Cloud features
│   ├── distributed_systems_validation.py # Raft + Vector Clocks
│   ├── two_phase_commit_validation.py # 2PC validation
│   ├── tandem_queue_validation.py # Two-stage validation
│   └── run_with_confidence.py # Statistical experiments (20 reps)
│
├── tests/                      # Unit tests (29 tests, all passing)
│   ├── test_erlang.py          # M/Ek/N validation
│   ├── test_queueing_laws.py   # Little's Law, stability
│   └── test_extreme_values.py  # EVT tests
│
├── debug/                      # Debugging scripts
└── visualization/              # Plot generation
```

## Mathematical Foundation

### The 15 Equations

#### Section 1: M/M/N Baseline (Equations 1-5)
1. **Utilization**: ρ = λ/(N·μ)
2. **P₀**: Erlang-C probability system empty
3. **Erlang-C**: Probability of queueing
4. **Lq**: Mean queue length
5. **Wq**: Mean waiting time (Little's Law)

#### Section 2: Heavy-Tailed Extension (Equations 6-10)
6. **Pareto PDF**: f(t) = α·k^α / t^(α+1)
7. **Mean**: E[S] = α·k/(α-1)
8. **Second Moment**: E[S²] = α·k²/(α-2)
9. **Coefficient of Variation**: C² = 1/(α-2)
10. **M/G/N Waiting Time**: Wq ≈ C(N,λ/μ)·(ρ/(1-ρ))·(E[S]/2)·(1+C²)

#### Section 3: Threading Models (Equations 11-15)
11. **Dedicated Max Connections**: Nmax = Nthreads/2
12. **Dedicated Throughput**: X = min(λ, (Nthreads/2)·μ)
13. **Shared Overhead**: μeff = μ/(1 + α·Nactive/Nthreads)
14. **Thread Saturation**: Psaturate = C(N,λ/μ)·ρ
15. **P99 Latency**: R99 ≈ E[R] + 2.33·σR

## Key Features

### 1. Type-Safe Configuration (Pydantic)
```python
from src.core.config import MMNConfig

config = MMNConfig(
    arrival_rate=100,      # λ = 100 msg/sec
    num_threads=10,        # N = 10 threads
    service_rate=12,       # μ = 12 msg/sec/thread
    sim_duration=1000,
    warmup_time=100,
    random_seed=42
)

# Automatic validation
print(f"Utilization: {config.utilization:.3f}")  # ρ = 0.833
```

### 2. Heavy-Tailed Distributions
```python
from src.core.distributions import ParetoService

# Heavy-tailed service time
pareto = ParetoService(alpha=2.5, scale=0.1)
print(f"Mean: {pareto.mean():.6f}")
print(f"CV²: {pareto.coefficient_of_variation():.2f}")
```

### 3. Analytical Models
```python
from src.analysis.analytical import MMNAnalytical

analytical = MMNAnalytical(
    arrival_rate=100,
    num_threads=10,
    service_rate=12
)

metrics = analytical.all_metrics()
print(f"Mean waiting time: {metrics['mean_waiting_time']:.6f} sec")
print(f"Mean queue length: {metrics['mean_queue_length']:.2f}")
```

### 4. Simulation Models
```python
from src.models.mmn_queue import run_mmn_simulation

# Run simulation
metrics = run_mmn_simulation(config)
stats = metrics.summary_statistics()

print(f"Simulated mean wait: {stats['mean_wait']:.6f} sec")
print(f"P99 response time: {stats['p99_response']:.6f} sec")
```

## Course Concept Integration

This project demonstrates key distributed systems concepts:

| Course Concept | Implementation |
|----------------|----------------|
| **Publish-Subscribe** | Message broker as pub-sub middleware |
| **Message Queues** | Queue length and waiting time modeling |
| **Threading Models** | Dedicated vs Shared (Ch. 7) |
| **Queueing Theory** | M/M/N, M/G/N, Erlang-C |
| **IPC** | Message passing overhead |
| **Performance Analysis** | Latency, throughput, utilization |

## Research Contribution

### Beyond Li et al. (2015):
1. **Heavy-tailed workloads**: Their model assumes exponential service times; we add Pareto, lognormal, and Weibull
2. **Threading models**: Explicit modeling of dedicated vs shared threading (from course Ch. 7)
3. **Analytical framework**: 15 equations vs their basic queueing model
4. **Validation**: Comprehensive simulation-based validation

### Key Findings (from experiments):
- Heavy tails (α=2.1) increase P99 latency by ~50% vs exponential
- Shared threading has 10-15% overhead but supports unlimited connections
- Dedicated threading: higher performance, limited to Nthreads/2 connections

## Tandem Queue Model (Li et al. 2015)

### Two-Stage Architecture

The tandem queue model represents a **two-stage broker→receiver** communication system:

```
Publishers → [Stage 1: Broker] → Network → [Stage 2: Receiver] → Consumers
             (n₁ servers, μ₁)    (D, p)    (n₂ servers, μ₂)
```

### Critical Insight: Stage 2 Load Amplification

**Key Equation:**
```
Λ₂ = λ/(1-p)
```

Due to transmission failures (probability p), **Stage 2 sees higher arrival rate** than Stage 1!

**Example:**
- λ = 100 msg/sec at broker
- p = 0.2 (20% failure rate)
- Λ₂ = 125 msg/sec at receiver (25% higher!)

### Quick Start

```python
from src.core.config import TandemQueueConfig
from src.models.tandem_queue import run_tandem_simulation
from src.analysis.analytical import TandemQueueAnalytical

# Configure two-stage system
config = TandemQueueConfig(
    arrival_rate=100,        # λ = 100 msg/sec
    n1=10, mu1=12,          # Stage 1: broker
    n2=12, mu2=12,          # Stage 2: receiver (needs more capacity!)
    network_delay=0.01,      # 10ms network delay
    failure_prob=0.2,        # 20% transmission failures
    sim_duration=1000,
    warmup_time=100
)

# Run simulation
results = run_tandem_simulation(config)
print(f"End-to-end latency: {results['mean_end_to_end']*1000:.2f} ms")

# Compare with analytical
analytical = TandemQueueAnalytical(
    lambda_arrival=100,
    n1=10, mu1=12,
    n2=12, mu2=12,
    network_delay=0.01,
    failure_prob=0.2
)

print(f"Analytical latency: {analytical.total_message_delivery_time()*1000:.2f} ms")
analytical.compare_stages()  # Shows Stage 2 load increase
```

### Run Tandem Queue Experiments

```bash
# Validate analytical model
python experiments/tandem_queue_validation.py

# Quick analytical validation
python debug/validate_tandem_analytical.py
```

### Key Formulas

See `TANDEM_QUEUE_EQUATIONS.md` for complete mathematical documentation.

**Essential equations:**
- Stage 2 arrival: `Λ₂ = λ/(1-p)`
- Stage 2 utilization: `ρ₂ = λ/((1-p)·n₂·μ₂)`
- Network time: `(2+p)·D_link`
- Total latency: `W₁ + S₁ + (2+p)·D + W₂ + S₂`

## Testing

```bash
# Quick test - all distributed systems features
./test_all.sh

# Unit tests - 29 tests covering queueing laws, Erlang, EVT
python3 -m pytest tests/ -v

# Individual experiments
python3 experiments/run_basic_experiment.py
python3 experiments/cloud_broker_simulation.py
python3 experiments/distributed_systems_validation.py
python3 experiments/two_phase_commit_validation.py
python3 experiments/tandem_queue_validation.py

# Complete rebuild (all tests + experiments + plots)
./rebuild_all.sh
```

See `TESTING_GUIDE.md` for detailed testing procedures.

## Performance Metrics

The system tracks:
- **Mean waiting time (Wq)**: Time in queue before service
- **Mean response time (R)**: Total time (wait + service)
- **P50, P95, P99 latencies**: Percentile metrics for SLAs
- **Queue length (Lq)**: Average messages waiting
- **Throughput**: Messages processed per second
- **Utilization (ρ)**: Fraction of time threads are busy

## References

1. **Li, J., Cui, Y., & Ma, Y. (2015)**. "Modeling Message Queueing Services with Reliability Guarantee in Cloud Computing Environment Using Colored Petri Nets." *Mathematical Problems in Engineering*, 2015.

2. **Kleinrock, L.** *Queueing Systems, Volume 1: Theory*. Wiley, 1975.

3. **Course Notes**: Distributed Systems, Chapter 7 (Threading Models), Chapter 15 (Publish-Subscribe)

## Implementation Status

### Completed Features

- [x] M/M/N, M/G/N, M/Ek/N queue models with analytical validation
- [x] Tandem queue (two-stage broker→receiver) with network failures
- [x] Threading model comparison (dedicated vs shared)
- [x] Heavy-tailed distributions (Pareto) with Erlang variance control
- [x] Distributed protocols: Raft, Vector Clocks, Two-Phase Commit
- [x] Cloud broker features: visibility timeout, replication, message ordering
- [x] In-order vs out-of-order message delivery
- [x] Network delay modeling with failure probability
- [x] CAP theorem analysis
- [x] Extreme Value Theory for tail latency
- [x] 29 unit tests (queueing laws, Erlang, EVT)
- [x] Statistical rigor: 20 replications with 95% confidence intervals
- [x] Analytical vs simulation comparison plots
- [x] Complete documentation (README, CLAUDE.md, MATHEMATICAL_GUIDE.md, TESTING_GUIDE.md)

### Future Enhancements

- [ ] Add more distribution types (hyperexponential, phase-type)
- [ ] Implement parameter optimization for different workloads
- [ ] Create interactive visualization dashboard
- [ ] Add Byzantine fault tolerance protocols
- [ ] Implement Paxos consensus algorithm

## Authors

- **Project**: Distributed Systems Performance Modeling
- **Course**: Advanced Distributed Systems
- **Based on**: Li et al. (2015) + Course material

## License

This is an academic project for educational purposes.

---

**Project Status**: COMPLETE AND VALIDATED ✓

**Core Implementation**: 100% Complete
- Configuration system (Pydantic with validation) ✓
- Distribution classes (Pareto, Erlang, Exponential) ✓
- Analytical models (all 15 equations implemented) ✓
- Queue models (M/M/N, M/G/N, M/Ek/N, Tandem) ✓
- Distributed protocols (Raft, Vector Clocks, 2PC) ✓
- Cloud broker features (visibility timeout, replication, ordering) ✓

**Validation & Testing**: 100% Complete
- 29 unit tests (all passing) ✓
- Integration tests (all passing) ✓
- Analytical vs simulation comparisons ✓
- Statistical rigor: 20 replications with 95% CI ✓
- Error validation: <10% simulation vs analytical ✓

**Documentation**: 100% Complete
- README.md (project overview) ✓
- CLAUDE.md (AI assistant guide) ✓
- MATHEMATICAL_GUIDE.md (equation derivations) ✓
- TESTING_GUIDE.md (testing procedures) ✓

**Last Updated**: 2025-11-15
