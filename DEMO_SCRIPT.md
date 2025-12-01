# Project Demo Script
**Goal:** Demonstrate the "Reality Gap" between standard models (M/M/n) and realistic heavy-tailed models (M/G/n), and show how your "Engineering Tools" solve it.

---

## Phase 0: Setup (One-Click)
**Terminal:**
```bash
cd /Users/himanshu_jain/273/distributed-systems-project
./start.sh
```
*Open http://localhost:4000 in your browser.*

---

## Phase 1: The Baseline (Control Center)
**Screen:** `Control Center`
**Action:**
1.  Start on the **Control Center**.
2.  Select **"Baseline (Standard)"** from the Scenario dropdown.
3.  **Say:** "We start with the baseline. This is the standard M/M/N model. Latency is stable at 200ms."

## Phase 2: The Hook (Control Center)
**Screen:** `Control Center` (The Storyteller)
**Action:**
1.  **Action:** Select **"The Crash (Pareto Workload)"** from the Scenario dropdown.
2.  **Observe:** The graph spikes red. The servers turn red.
3.  **Say:** "Watch what happens when a heavy-tailed workload hits. The system crashes. Standard math didn't predict this."

## Phase 3: The Fix (Capacity Planner)
**Screen:** `Capacity Planner`
**Action:**
1.  Navigate to **Capacity Planner**.
2.  Click **"Inverse Solver"**.
3.  **Input:** Target Latency = 200ms, Traffic Load = 400, Server Capacity = 30.
4.  **Observe:** It calculates "Required Servers: 14".
5.  **Say:** "How do we fix it? We use the Inverse Solver. It tells us exactly how many servers we need to handle the load."

## Phase 4: The Consequence (The Blast Radius)
**Screen:** `The Blast Radius`
**Action:**
1.  Navigate to **The Blast Radius**.
2.  Toggle Workload to **"Bursty"**.
3.  **Observe:** Node 2 has much bigger spikes than Node 1.
4.  **Say:** "Why did it crash so hard? Variance Amplification. A small spike here causes a massive explosion downstream."

## Phase 5: The Proof (Reality Gap Explorer)
**Screen:** `Reality Gap Explorer`
**Action:**
1.  Navigate to **Reality Gap Explorer**.
2.  Drag the **Variance Slider** to the right.
3.  **Observe:** The Red Line (Reality) pulls away from the Blue Line (Math).
4.  **Say:** "This is the Reality Gap. The math (Blue) says we're fine. Reality (Red) says we're dead. Our simulation tells the truth."

---

## Q&A Cheat Sheet (The "Defense Translation Table")

| If Professor Says... | You Say... |
| :--- | :--- |
| "Your throughput is low." | "I modeled finite buffers and network RTT, which creates realistic backpressure. It's a trade-off for fidelity." |
| "Why is the graph so erratic?" | "That's the signature of a Pareto distribution. If it were smooth, it would be wrong." |
| "Why not use CPN Tools?" | "SimPy allows us to model complex protocols like Raft and 2PC, which are impossible in CPN." |
