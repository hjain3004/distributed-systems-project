# 🚀 Demo Instruction Manual
**For: First-Time Users / Presenters**

This guide assumes **zero prior knowledge**. Follow these steps exactly to run the "Distributed Systems Performance Modeling" demo.

---

## 1. Prerequisites (Do this once)

Ensure you have the following installed:
1.  **Node.js 18+** (`node -v`)
2.  **Python 3.11+** (`python3 --version`)

---

## 2. Startup (The "One-Click" Launch)

We have automated the entire startup process.

1.  Open your terminal.
2.  Navigate to the project folder:
    ```bash
    cd distributed-systems-project
    ```
3.  Run the start script:
    ```bash
    ./start.sh
    ```

**What happens next:**
- The **Backend** will start on Port **3100**.
- The **Frontend** will start on Port **4000**.
- Your default browser should automatically open to `http://localhost:4000`.

*(If the browser doesn't open, manually visit [http://localhost:4000](http://localhost:4000))*

---

## 3. The Demo Flow (Step-by-Step)

The demo is structured as a narrative: **The Crash -> The Fix -> The Consequence -> The Proof.**

### Step 1: The Baseline (The "Before" State)
**Goal:** Establish what "Normal" looks like.

1.  **Navigate**: Click **"Control Center"** in the sidebar.
2.  **Action**:
    *   Select **"Baseline (Standard)"** from the Scenario dropdown.
3.  **Observe**:
    *   **Latency**: Stable at **~200ms**.
    *   **Status**: Green / Stable.
4.  **Say**: *"This is our baseline. Standard M/M/N model. Everything looks healthy."*

### Step 2: The Hook - "The Crash" (The Problem)
**Goal:** Viscerally demonstrate a system crash due to heavy-tailed workloads.

1.  **Action**:
    *   Select **"The Crash (Pareto Workload)"** from the Scenario dropdown.
2.  **Observe**:
    *   The **Latency Graph** (red line) will spike dramatically (from ~200ms to >1.5s).
    *   The **Server Topology** (circles) will turn **RED**.
    *   The **"Oh Sh*t" Status** will flash.
3.  **Say**: *"But watch what happens when a heavy-tailed workload hits. The system crashes."*

### Step 2: The Fix - "Capacity Planner" (The Solution)
**Goal:** Show how to calculate the correct capacity to prevent the crash.

1.  **Navigate**: Click **"Capacity Planner"** in the sidebar.
2.  **Action**:
    *   Click the **"Inverse Solver"** tab.
    *   **Target Latency**: Enter `200` (ms).
    *   **Traffic Load**: Enter `400` (req/s).
    *   **Server Capacity**: Enter `30` (req/s).
3.  **Observe**:
    *   The tool calculates: **"Recommended Servers: 14"**.
4.  **Say**: *"Instead of guessing, we use the Inverse Solver. It tells us exactly how many servers we need to maintain 200ms latency."*

### Step 3: The Consequence - "The Blast Radius" (Chain Reaction)
**Goal:** Show how failures propagate downstream.

1.  **Navigate**: Click **"The Blast Radius"** in the sidebar.
2.  **Action**:
    *   Toggle **"Workload"** to **"Bursty (Pareto)"**.
3.  **Observe**:
    *   **Node 1 Graph**: Shows small spikes.
    *   **Node 2 Graph**: Shows **MASSIVE** spikes (Amplification).
4.  **Say**: *"A small hiccup in the first service causes a massive explosion in the second service. This is Variance Amplification."*

### Step 4: The Proof - "Reality Gap Explorer" (The Evidence)
**Goal:** Prove that standard math is wrong.

1.  **Navigate**: Click **"Reality Gap Explorer"** in the sidebar.
2.  **Action**:
    *   Drag the **"Variance (Cv²)"** slider to the **Right** (increase variance).
3.  **Observe**:
    *   **Blue Line (Theory)**: Stays flat (predicts low latency).
    *   **Red Line (Reality)**: Shoots up (shows high latency).
    *   The gap between them widens.
4.  **Say**: *"This gap is why systems crash. The math says we're safe (Blue), but reality says we're dead (Red)."*

---

## 4. Troubleshooting

**Q: The browser says "Connection Refused".**
A: Wait 10 seconds. The backend takes a moment to start. Refresh the page.

**Q: Port 3100 or 4000 is already in use.**
A: The script will try to kill the old processes. If it fails, run:
   ```bash
   lsof -ti:3100,4000 | xargs kill -9
   ```
   Then run `./start.sh` again.

**Q: The graphs aren't moving.**
A: Ensure the backend is running. Check the terminal window where you ran `./start.sh` for errors.

---

**Demo Complete!** 🚀
