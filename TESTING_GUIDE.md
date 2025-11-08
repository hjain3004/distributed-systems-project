# Testing Guide - Distributed Systems Features

## Quick Start - Test Everything

Run all validations at once:

```bash
# Test 1: Cloud Message Broker (visibility timeout, replication, ordering)
python3 experiments/cloud_broker_simulation.py

# Test 2: Distributed Systems Protocols (Raft, Vector Clocks, CAP)
python3 experiments/distributed_systems_validation.py

# Test 3: Two-Phase Commit Protocol
python3 experiments/two_phase_commit_validation.py

# Test 4: CAP Theorem Analysis (standalone)
python3 -m src.analysis.cap_analysis
```

---

## Individual Feature Tests

### 1. Visibility Timeout & Message Broker

```bash
python3 experiments/cloud_broker_simulation.py
```

**What to expect:**
- ✅ Experiment 1: Visibility timeout impact (10, 30, 60, 120 seconds)
- ✅ Experiment 2: Replication factor impact (1x, 2x, 3x)
- ✅ Experiment 3: Ordering mode comparison (in-order vs out-of-order)

**Expected output:**
```
EXPERIMENT: Visibility Timeout Impact
Testing visibility timeout = 10 seconds...
  Success rate: 65.2%
  Mean latency: 18.45 sec
  Mean retries: 1.23

...

✓ All experiments completed
✓ CSV files generated in experiments/
```

**Success indicators:**
- Higher visibility timeout → higher success rate
- Higher replication factor → better reliability
- Out-of-order delivery → similar/better performance

---

### 2. Raft Consensus Protocol

```bash
python3 experiments/distributed_systems_validation.py
```

**What to expect:**
- ✅ Experiment 1: Raft leader election across 5 nodes
- ✅ Experiment 2: Log replication from leader to followers

**Expected output:**
```
EXPERIMENT 1: Raft Leader Election
Node       State           Term     Leader     Elections Won
----------------------------------------------------------------------
0          follower        1        4          0
1          follower        1        4          0
2          follower        1        4          0
3          follower        1        4          0
4          leader          1        4          1

✓ Single leader elected: True
✓ All nodes agree on leader: True
```

**Success indicators:**
- Exactly 1 leader elected
- All nodes agree on same leader
- All followers have same term as leader

---

### 3. Vector Clocks & Causality

This runs automatically as part of `distributed_systems_validation.py`:

**Expected output:**
```
EXPERIMENT 3: Vector Clocks and Causality
E0: Process 0 local event → VC = [1, 0, 0]
E1: Process 0 sends message → VC = [2, 0, 0]
E2: Process 1 receives message → VC = [2, 1, 0]

CAUSALITY ANALYSIS
E0 → E1 (same process)         → happened_before
E1 → E2 (send-receive)         → happened_before
E2 || E4 (concurrent)          → concurrent

✓ Send-receive causality: True
✓ Concurrent detection: True
```

**Success indicators:**
- Send-receive relationships detected as "happened_before"
- Independent events detected as "concurrent"
- Vector clocks updated correctly

---

### 4. Two-Phase Commit (2PC)

```bash
python3 experiments/two_phase_commit_validation.py
```

**Expected output:**
```
EXPERIMENT 1: 2PC - All Participants Vote YES
Coordinator Metrics:
  Total transactions: 10
  Committed: 10
  Aborted: 0
  Commit rate: 100.0%

✓ All transactions committed: True
✓ No aborts: True

EXPERIMENT 2: 2PC - Some Participants Vote NO
Coordinator Metrics:
  Committed: 5
  Aborted: 15
  Commit rate: 25.0%

✓ Atomic commit guarantee: All-or-nothing commits enforced
```

**Success indicators:**
- 100% commit rate when all vote YES
- Proper aborts when participants vote NO
- All participants execute same decision (atomicity)

---

### 5. CAP Theorem Analysis

```bash
python3 -m src.analysis.cap_analysis
```

**Expected output:**
```
CAP THEOREM ANALYSIS - Cloud Message Brokers

MODE: CP
Consistency:          Strong (linearizable)
Availability:         Reduced during partitions
Use Cases:
  - Financial transactions
  - Banking systems

MODE: AP
Consistency:          Eventual (may see stale data)
Availability:         Always available
Use Cases:
  - AWS SQS / Azure Queue Storage (as in paper)

RECOMMENDATION FOR CLOUD MESSAGE BROKER
AWS SQS: AP mode
  - Favors availability over strict consistency
```

---

## Quick Verification Script

Create a quick test to verify all components:

```bash
# Create test script
cat > test_all.sh << 'EOF'
#!/bin/bash

echo "========================================="
echo "Testing Distributed Systems Features"
echo "========================================="

echo -e "\n1. Testing Cloud Message Broker..."
python3 experiments/cloud_broker_simulation.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Cloud broker tests PASSED"
else
    echo "   ✗ Cloud broker tests FAILED"
fi

echo -e "\n2. Testing Distributed Systems (Raft + Vector Clocks)..."
python3 experiments/distributed_systems_validation.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Distributed systems tests PASSED"
else
    echo "   ✗ Distributed systems tests FAILED"
fi

echo -e "\n3. Testing Two-Phase Commit..."
python3 experiments/two_phase_commit_validation.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ 2PC tests PASSED"
else
    echo "   ✗ 2PC tests FAILED"
fi

echo -e "\n========================================="
echo "All tests completed!"
echo "========================================="
EOF

chmod +x test_all.sh
./test_all.sh
```

---

## Interactive Python Testing

You can also test components interactively:

### Test Visibility Timeout
```python
import sys
sys.path.insert(0, '.')

import simpy
from src.models.cloud_message import CloudMessage
from src.models.visibility_timeout import VisibilityTimeoutManager

# Create environment
env = simpy.Environment()

# Create visibility timeout manager
manager = VisibilityTimeoutManager(env)

# Add message
msg = CloudMessage(id=1, content="Test", arrival_time=0, visibility_timeout=30)
manager.add_message(msg)

# Receive message (makes invisible)
received = manager.receive_message()
print(f"Received: {received.id}, State: {received.state}")

# Run simulation
env.run(until=10)

# Check metrics
print(f"Metrics: {manager.get_metrics()}")
```

### Test Vector Clocks
```python
from src.models.vector_clocks import VectorClock, CausalityTracker

# Create 3-process system
tracker = CausalityTracker(num_processes=3)

# Process 0: local event
vc1 = tracker.local_event(0)
print(f"P0 local event: {vc1}")

# Process 0: send to Process 1
vc2 = tracker.send_event(0)
print(f"P0 sends: {vc2}")

# Process 1: receive
vc3 = tracker.receive_event(1, vc2)
print(f"P1 receives: {vc3}")

# Check causality
relationship = tracker.check_causality(0, 2)
print(f"Relationship: {relationship}")  # Should be "happened_before"
```

### Test Raft Consensus
```python
import simpy
from src.models.raft_consensus import RaftCluster

# Create cluster
env = simpy.Environment()
cluster = RaftCluster(env=env, num_nodes=5)

# Run election
env.run(until=50)

# Check leader
leader = cluster.get_leader()
if leader:
    print(f"Leader elected: Node {leader.node_id}")
else:
    print("No leader yet")

# Get metrics
metrics = cluster.get_cluster_metrics()
for m in metrics:
    print(f"Node {m['node_id']}: {m['state']}, term={m['term']}")
```

---

## Checking Results

### Generated Files

After running experiments, check for these files:
```bash
ls -lh experiments/*.csv
```

Expected files:
- `visibility_timeout_results.csv`
- `replication_factor_results.csv`
- `ordering_mode_results.csv`

### View Results
```bash
# View visibility timeout results
cat experiments/visibility_timeout_results.csv

# View replication factor results
cat experiments/replication_factor_results.csv
```

---

## Troubleshooting

### If tests fail:

1. **Check Python version:**
```bash
python3 --version  # Should be 3.9+
```

2. **Check dependencies:**
```bash
pip list | grep -E "simpy|numpy|pandas|matplotlib|seaborn"
```

3. **Install missing dependencies:**
```bash
pip install simpy numpy pandas matplotlib seaborn
```

4. **Run with verbose output:**
```bash
python3 experiments/cloud_broker_simulation.py 2>&1 | tee test_output.log
```

5. **Check for import errors:**
```bash
python3 -c "from src.models.raft_consensus import RaftCluster; print('Raft OK')"
python3 -c "from src.models.vector_clocks import VectorClock; print('Vector Clocks OK')"
python3 -c "from src.models.two_phase_commit import TwoPhaseCommitCluster; print('2PC OK')"
```

---

## Expected Runtime

- Cloud broker simulation: ~5-10 seconds
- Distributed systems validation: ~10-15 seconds
- Two-Phase Commit: ~5 seconds
- CAP analysis: <1 second

**Total runtime: ~25-35 seconds**

---

## Success Criteria

✅ All experiments complete without errors
✅ CSV files generated in `experiments/` directory
✅ Raft elects exactly 1 leader
✅ Vector clocks detect causality correctly
✅ 2PC enforces atomicity (all commit or all abort)
✅ CAP analysis shows trade-offs for CP vs AP modes

---

## Next Steps After Testing

1. Review generated CSV files for experimental data
2. Check `DISTRIBUTED_SYSTEMS_FEATURES.md` for detailed documentation
3. Run with different parameters to see trade-offs
4. Generate visualizations (if needed)

---

*Last updated: 2025-11-07*
