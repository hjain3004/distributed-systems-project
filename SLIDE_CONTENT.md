# Presentation Slide Template
**Instructions:** Open PowerPoint/Google Slides. Create 8 slides. Copy the content below for each slide.

---

## Slide 1: Title Slide
*   **Title:** Reliability and Performance in Distributed Message Queues
*   **Subtitle:** Analyzing Heavy-Tailed Workloads in Cloud Systems
*   **Your Name:** [Your Name]
*   **Course:** Distributed Systems (CS 273)

---

## Slide 2: The Problem
*   **Title:** The Challenge of Reliable Cloud Messaging
*   **Bullet Points:**
    *   Cloud systems must guarantee message delivery ("At-Least-Once").
    *   Network failures cause retransmissions, creating extra load.
    *   **The Gap:** Existing models (Li et al. 2015) assume "Exponential" service times.
    *   **Reality:** Real cloud workloads are "Heavy-Tailed" (Pareto) – rare, huge jobs block the queue.

---

## Slide 3: Base Paper Validation
*   **Title:** Validating the Baseline Model
*   **Bullet Points:**
    *   We reproduced the "Tandem Queue" model from Li et al. (2015).
    *   Verified "Traffic Inflation" logic: $\Lambda_{receiver} = \lambda / (1-p)$.
    *   **Result:** Our simulation matches the paper's results with <15% error.
*   **Image:** `results/plots/figure11_comparison.png`
*   **Speaker Note:** "First, I proved I could reproduce the base paper's results accurately."

---

## Slide 4: The Reality Gap
*   **Title:** The "Reality Gap" in Performance
*   **Bullet Points:**
    *   We tested the model against a realistic Heavy-Tailed workload.
    *   **Paper (M/M/n):** Predicts 0.16s latency (Too Optimistic).
    *   **Simulation (M/G/n):** Shows 0.19s latency (The Truth).
    *   **Conclusion:** The paper underestimates average latency by 14%.
*   **Image:** `results/plots/reality_gap.png`

---

## Slide 5: Tail Risk (The Critical Finding)
*   **Title:** Tail Latency: The Hidden Danger
*   **Bullet Points:**
    *   Average latency looks okay, but **P99 (Tail) Latency** is critical for SLAs.
    *   **Paper Prediction:** 4.25s (Normal Approximation).
    *   **Simulation Reality:** 7.81s (Extreme Value Theory).
    *   **Impact:** The paper underestimates tail risk by **~45%**.
*   **Image:** `results/plots/tail_risk.png`
*   **Speaker Note:** "This is the most important slide. The paper's math fails to predict the extreme delays that crash systems."

---

## Slide 6: Scientific Rigor
*   **Title:** Verifying the Results (Convergence)
*   **Bullet Points:**
    *   Is this just statistical noise? No.
    *   We ran simulations with **400,000 messages** (100x more than the paper).
    *   **Result:** The P99 latency stabilizes at ~12.2s.
*   **Image:** `results/plots/convergence_test.png`

---

## Slide 7: The Solution
*   **Title:** Mitigation: Taming the Tail
*   **Bullet Points:**
    *   How do we fix the high latency?
    *   **N=1:** System is overwhelmed (12.3s).
    *   **N=2:** Adding 1 server drops latency to **0.90s**.
    *   **Result:** A **93% performance improvement**.
*   **Image:** `results/plots/mitigation_scaling.png`

---

## Slide 8: Conclusion
*   **Title:** Summary & Contributions
*   **Bullet Points:**
    *   **Validated:** Reproduced Li et al. (2015) successfully.
    *   **Identified:** The paper fails for Heavy-Tailed workloads (45% error).
    *   **Solved:** Built an M/G/n simulation to correctly predict and mitigate tail risks.
    *   **Takeaway:** Simulation is essential for robust cloud system design.
