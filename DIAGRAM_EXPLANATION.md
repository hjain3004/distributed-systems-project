# Diagram Explanations for Presentation

This document contains the **comprehensive** speaker scripts for your two key architecture diagrams. Read these sections while presenting the respective slides.

---

## 1. System Architecture (The "Big Picture")

**Visual Reference:** `architecture_diagram.png`
**Goal:** Explain the System Design, the Technology Stack, and the Data Flow.

### 🗣️ Speaker Script

"This diagram represents the high-level architecture of our **TraceBreaker** platform. It is designed as a modern distributed system with a clear separation between the **Control Plane** (Frontend) and the **Data Plane** (Backend).

#### **A. The Technology Stack (Left & Right)**
Before we dive into the logic, let's look at the technologies that power this system:

*   **The Frontend (Port 4000)**:
    *   Built with **React 18** and **TypeScript** for type-safe, component-based UI.
    *   Styled with **Tailwind CSS** and **Shadcn UI** for a professional, accessible design system.
    *   Data visualization is handled by **Recharts**, allowing us to render high-frequency telemetry at 60 FPS.
    *   State management uses **React Hooks** (`useRef`) to handle the simulation loop without blocking the main thread.

*   **The Backend (Port 3100)**:
    *   Powered by **FastAPI**, a high-performance asynchronous Python framework.
    *   The core simulation engine is **SimPy**, a discrete-event simulation library. We chose SimPy because it natively models process interactions—like threads blocking for I/O—which is essential for simulating complex protocols like 2PC.
    *   **NumPy** handles the heavy statistical lifting (Pareto distributions, percentiles) to ensure mathematical accuracy.

#### **B. The Logical Flow (Center Box)**
The simulation engine follows a strict pipeline designed to mimic a real-world microservices cluster:

1.  **Admission Controller (The Guard)**:
    *   This is our first line of defense. It implements **Adaptive Load Shedding**.
    *   Notice the dashed line labeled **'503 Shed'**. When the system hits its concurrency limit, we don't just queue requests forever; we reject them immediately. This prevents the 'Death Spiral' we saw in the crash scenario.

2.  **Smart Router (The Brain)**:
    *   Accepted requests are passed to the Load Balancer.
    *   We use the **JSQ (Join-the-Shortest-Queue)** algorithm here. Unlike Round-Robin, JSQ actively monitors the queue depth of every worker and routes traffic to the least loaded node.

3.  **Execution Layer (The Workers)**:
    *   This is where we model **Heterogeneity**. We have **Fast Workers (Green)** and **Legacy Workers (Red)**.
    *   **The Critical Optimization**: Look at the dashed line labeled **'Work Stealing'**. This represents our custom scheduler logic. If a Fast Worker finishes its tasks, it doesn't go idle; it reaches into the Legacy Worker's queue and 'steals' a job. This is how we solved the heterogeneity bottleneck without buying more hardware.

4.  **Reliability Layer (The Cost)**:
    *   Finally, we have the **Consensus Module**.
    *   We simulate a **2PC (Two-Phase Commit)** protocol. The **'WAL Database'** cylinder represents the Write-Ahead Log.
    *   This component adds realistic **I/O Latency** to the system. It forces every request to wait for a 'disk write' simulation, proving that strong consistency is never free."

---

## 2. Formal Queueing Network (The "Math")

**Visual Reference:** `Queueing_Network_Diagram.png`
**Goal:** Prove the mathematical rigor and formal validity of the simulation.

### 🗣️ Speaker Script

"To validate that our simulation isn't just 'random numbers', we modeled it as a formal **Closed Queueing Network**. This diagram maps the code directly to Queueing Theory notation.

#### **A. Admission Stage (Input Modeling)**
*   **Source ($\lambda_{in}$)**: This generates our traffic. We use a **Pareto Distribution** (Heavy-Tailed) rather than a standard Poisson process. This allows us to model 'bursty' real-world traffic where $P(X > x) \sim x^{-\alpha}$.
*   **Q1_Buff [Capacity K]**: This represents a **G/G/1/K** queue. The 'K' is crucial—it denotes a finite buffer.
*   **$P_{drop}$**: This path represents the **Loss Probability**. Mathematically, when $N(t) = K$, any new arrival is dropped. This formalizes our Load Shedding logic: $\lambda_{eff} = \lambda_{in} \times (1 - P_{drop})$.

#### **B. Execution Stage (Service Modeling)**
*   **Router ($\{r, 1-r\}$)**: The diamond shape represents our routing probability. Under JSQ, $r$ is dynamic—it changes based on the state of $QF$ vs $QS$.
*   **Heterogeneity ($\mu_f$ vs $\mu_s$)**: We explicitly model two distinct service rates.
    *   $\mu_f$: Service rate of Fast Servers (e.g., 15 req/s).
    *   $\mu_s$: Service rate of Slow Servers (e.g., 3 req/s).
*   **Stealing (The Cross-Over)**: The dashed diagonal arrow is the most mathematically interesting part. It represents a state-dependent transition.
    *   If $QF(t) = 0$ AND $QS(t) > 0$, a job moves from $QS \to SF$.
    *   This effectively increases the service rate of the slow queue by utilizing the spare capacity of the fast server.

#### **C. Synchronization Stage (Consistency Modeling)**
*   **Sync_Svr ($\mu_{sync}$)**: This node represents the **Consensus Barrier**.
*   In a distributed system, a transaction isn't done when the worker finishes; it's done when the log is committed.
*   We model this as a single server with rate $\mu_{sync}$, which represents the throughput limit of the consensus leader (e.g., the Raft leader or 2PC coordinator).
*   **Ack/Release**: The dashed feedback loop closes the system, signaling that resources can be freed.

**Conclusion**:
By mapping our code to this formal model, we can prove that our simulation results align with theoretical bounds for **Heterogeneous M/M/n** systems with **Work Stealing**."
