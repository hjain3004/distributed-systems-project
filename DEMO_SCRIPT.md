# Project Demo Script
**Goal:** Demonstrate the "Reality Gap" between standard models (M/M/n) and realistic heavy-tailed models (M/G/n), and show how your Tandem Queue simulation solves it.

---

## Phase 0: Setup (Before Recording)
**Terminal 1 (Backend):**
```bash
cd /Users/himanshu_jain/273/distributed-systems-project
python3 start_backend.py
```

**Terminal 2 (Frontend):**
```bash
cd /Users/himanshu_jain/273/distributed-systems-project/frontend
npm run dev
```
*Open http://localhost:5173 in your browser.*

---

## Phase 1: The Hook (Dashboard)
**Screen:** `Dashboard` (Home Page)
**Action:**
1.  Start on the Dashboard. Point out the modern, clean UI (Shadcn/Tailwind).
2.  **Say:** "This is the Distributed Systems Modeling Platform. It allows us to compare theoretical models against real-world simulations."
3.  Highlight the three main modules: M/M/N (Standard), M/G/N (Advanced), and Comparison.

## Phase 2: The Baseline (M/M/N Calculator)
**Screen:** `M/M/N Calculator`
**Action:**
1.  Click "Open Calculator" on the M/M/N card.
2.  **Input:**
    *   Arrival Rate ($\lambda$): 30
    *   Service Rate ($\mu$): 10
    *   Servers ($N$): 4
3.  **Observe:**
    *   Utilization ($\rho$): 0.75 (75%)
    *   Mean Wait Time: Low (e.g., ~0.02s)
4.  **Say:** "This is the standard model used in the base paper. It assumes everything is smooth (Exponential). The wait times are very low."

## Phase 3: The Problem (M/G/N Calculator)
**Screen:** `M/G/N Calculator`
**Action:**
1.  Navigate to "M/G/N Calculator".
2.  **Input:**
    *   Arrival Rate: 30
    *   Service Rate: 10
    *   Servers: 4
    *   **CV² (Variability):** Change from 1 (Exponential) to **10 (Heavy Tail)**.
3.  **Observe:**
    *   Mean Wait Time: **Explodes** (increases by ~5-10x).
4.  **Say:** "But real cloud systems have 'Heavy Tails'. When we increase the variability ($CV^2$), the standard model breaks. The wait times skyrocket."

## Phase 3b: The Explosion (Interactive Demo)
**Action:**
1.  Drag the **Shape Parameter ($\alpha$)** slider left to **2.1**.
2.  **Observe:**
    *   **Variability ($CV^2$)** jumps to **4.76**.
    *   **Penalty Factor** jumps to **2.88x**.
    *   **Mean Wait** jumps to **~147ms** (3x higher than baseline!).
3.  **Say:** "Watch what happens when I make the tail slightly heavier ($\alpha=2.1$). The variability explodes to 4.76. Suddenly, our wait time triples. This is the 'Reality Gap'—standard models miss this completely."

## Phase 4: The Proof (Comparison Page)
**Screen:** `Model Comparison`
**Action:**
1.  Navigate to "Model Comparison".
2.  **Input:** Same parameters ($\lambda=30, \mu=10, N=4$).
3.  **Click:** "Run Comparison".
4.  **Show Chart:** Point to the bar chart showing "Analytical" vs "Simulation".
5.  **Say:** "Here we compare the math against a real discrete-event simulation. You can see the simulation confirms the high latency## Phase 6: The "Cost of Consistency" (The Save)

**Goal:** If the professor asks "What about In-Order delivery?", you use this.

**Action:**
1.  Open the **Tandem Queue** page.
2.  Scroll down to the **"Consistency Model"** toggle.
3.  Say: *"We also investigated the cost of strict ordering."*
4.  Flip the switch to **"In-Order"**.

**Observation:**
*   Latency **increases** (approx 13-15%).
*   Explain: *"This is the **Head-of-Line Blocking** effect. Fast messages get stuck behind slow ones."*

**The "Mic Drop" Line:**
*"Our experiments showed that enforcing strict FIFO adds ~13% latency overhead. This validates why many cloud systems prefer eventual consistency (Out-of-Order) for higher throughput."*

---

## Q&A Cheat Sheet
See `DEMO_TALKING_POINTS.md` for detailed answers."

## Phase 5: The Solution (Tandem Queue)
**Screen:** `Tandem Queue Model`
**Action:**
1.  Set **Global Arrival ($\lambda$)** to **31**.
2.  Set **Failure Probability ($p$)** to **10%**.
3.  **Say:** "Finally, here is our contribution: The Tandem Queue Model."
4.  **Point to 'Traffic Inflation':** "Look at this. We send **31** requests, but Stage 2 receives **34.4**. Why? Because of the 10% retries. We call this **'Traffic Inflation'**."
5.  **Point to Utilization:** "Stage 1 is healthy at **77%**, but Stage 2 is overheating at **86%**. This is the hidden danger—retries kill your downstream services first."
6.  **Conclusion:** "Our model predicts this cascading failure *before* it happens, allowing engineers to provision extra capacity for Stage 2." Even with 10% failure, our simulation accurately predicts the load."

---

## Demo Tips
*   **Keep it moving:** Don't spend too long on one screen.
*   **Focus on the Delta:** The most important thing is the *difference* between M/M/N and M/G/N.
*   **Use the Visuals:** Point to the charts, not just the numbers.
