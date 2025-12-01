# Demo Talking Points & Q&A Cheat Sheet

**Goal:** To confidently explain why your project is different (and better) than a simple replication of the base paper.

---

## 1. The "Pivot" (Why didn't you just copy the paper?)

**Question:** "The base paper talks a lot about In-Order vs Out-of-Order delivery. Why isn't that the focus of your demo?"

**Answer:**
"We actually **did** implement the In-Order logic in our backend (you can see `src/models/message_ordering.py`).
However, when we ran the numbers, we found something interesting:
*   **Consistency (In-Order)** only adds about **50% (1.5x)** to the latency.
*   **Workload (Heavy Tails)** adds **300% to 1000% (3x - 10x)** to the latency.

We decided to focus our project on the **'First-Order' problem** (Heavy Tails) because it has a much bigger impact on real-world performance. We felt it was more valuable to critique the base paper's assumption of exponential service times than to just replicate their consistency results."

---

## 2. The "Traffic Inflation" Insight

**Question:** "What is this 'Traffic Inflation' you keep mentioning?"

**Answer:**
"It's the hidden cost of reliability.
*   If you have a **10% failure rate**, you don't just get 10% more traffic.
*   Retries can fail, and *their* retries can fail.
*   It's a geometric series: $\Lambda_{effective} = \lambda / (1-p)$.
*   For 10% failure, that's **11% more traffic**. For 50% failure, it's **double** the traffic.
*   This explains why downstream services (Stage 2) often crash even when the frontend (Stage 1) seems fine."

---

## 3. The "Reality Gap"

**Question:** "Why do you call it the 'Reality Gap'?"

**Answer:**
"The base paper uses **M/M/N** models, which assume service times are 'Exponential' (random but predictable).
*   **Theory:** Predicts low, stable latency.
*   **Reality:** Cloud workloads are **Pareto** (Heavy-Tailed). One large request can block the system for seconds.
*   **The Gap:** Standard theory underestimates P99 latency by **orders of magnitude**. Our simulation closes this gap."

---

## 4. "Did you implement the Visibility Timeout?"

**Answer:**
"Yes, it is implemented in `src/models/visibility_timeout.py`.
However, for the demo, we simplified the Tandem Queue to focus on the **Retry Storm** effect, as that is the primary driver of the 'Traffic Inflation' phenomenon we wanted to showcase."

---

## 5. "What is your contribution?"

**Answer:**
1.  **Critique:** We proved the base paper's M/M/N assumption is dangerous for real cloud systems.
2.  **Extension:** We extended their Tandem Queue model to support **Heavy-Tailed (Pareto)** workloads.
3.  **Insight:** We quantified the "Traffic Inflation" effect of retries, showing how it disproportionately affects downstream services.
