# Diagram Explanations for Presentation

This document contains the speaker scripts for your two key architecture diagrams. Read these sections while presenting the respective slides.

---

## 1. System Architecture (The "Big Picture")

**Visual Reference:** `architecture_diagram.png`
**Goal:** Explain *what* we built and how the components interact.

### 🗣️ Speaker Script

"This diagram represents the high-level architecture of our **TraceBreaker** platform. It is designed as a modern distributed system with a clear separation between the Control Plane (Frontend) and the Data Plane (Backend).

**1. The Feedback Loop (Top & Bottom)**
The most important feature here is the **Interactive Feedback Loop**.
*   At the top, you see the **Reality Gap Loop**: The Client (User) defines the workload parameters in the Dashboard.
*   At the bottom, the system streams real-time telemetry back to the Dashboard.
*   This allows us to visualize the 'Reality Gap'—the difference between theoretical models and actual system behavior—in real-time.

**2. The Simulation Engine (Center Box)**
The core logic resides in the Backend (Port 3100). It follows a strict pipeline:
*   **Admission Controller**: This is our first line of defense. It implements **Adaptive Load Shedding**. You can see the '503 Shed' dashed line—if the system is overloaded, we reject requests immediately to prevent a crash.
*   **Smart Router**: Accepted requests go here. We use the **JSQ (Join-the-Shortest-Queue)** algorithm to intelligently balance load between our workers.
*   **Execution Layer**: This is where the heterogeneity lives. We have **Fast Workers (Green)** and **Legacy Workers (Red)**. Notice the dashed line for **Work Stealing**—this is a critical optimization where idle fast workers help out the struggling legacy nodes.

**3. The Reliability Layer (Right)**
Finally, every request must be committed. We simulate a **2PC (Two-Phase Commit)** protocol. The 'WAL Database' cylinder represents the Write-Ahead Log. This adds realistic latency to the system, simulating the cost of strong consistency."

---

## 2. Formal Queueing Network (The "Math")

**Visual Reference:** `Queueing_Network_Diagram.png`
**Goal:** Prove the mathematical rigor behind the simulation.

### 🗣️ Speaker Script

"To validate our simulation, we modeled it as a formal **Closed Queueing Network**. This diagram maps directly to the code we just saw.

**1. Admission Stage (Left)**
*   **Source**: This generates our **Pareto Workload** ($\lambda_{in}$), representing the bursty traffic.
*   **Q1_Buff**: This is a finite buffer with capacity $K$.
*   **$P_{drop}$**: This arrow represents the probability of a drop. If $Q1$ is full, the request follows this path and exits the system. This mathematically models our **Load Shedding**.

**2. Execution Stage (Center)**
*   **Router**: The diamond shape splits traffic ($r$ vs $1-r$) based on our load balancing logic.
*   **Heterogeneity**: We explicitly model two service rates: $\mu_f$ for Fast Servers and $\mu_s$ for Slow Servers.
*   **Stealing**: The dashed diagonal arrow is the most interesting part. It shows flow moving from the **Slow Queue ($QS\_Buff$)** to the **Fast Server ($SF\_Svr$)**. This formally captures the **Work Stealing** mechanism, where capacity is dynamically reallocated.

**3. Synchronization Stage (Right)**
*   **Sync_Svr**: All completed tasks must pass through this final node. This represents the **Consensus Module**.
*   It has its own service rate $\mu_{sync}$, which models the latency of the Two-Phase Commit protocol.
*   The **Ack/Release** dashed line closes the loop, signaling that the transaction is durable and the client can be notified.

**Conclusion**
By mapping our complex distributed system to this formal network, we were able to derive the theoretical bounds (the 'Blue Line' in our graphs) and prove that our simulation results are statistically valid."
