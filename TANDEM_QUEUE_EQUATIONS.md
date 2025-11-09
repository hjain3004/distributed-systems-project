# Tandem Queue Equations - Li et al. (2015)

## System Architecture
```
Publishers --λ--> [Stage 1: Broker] --network--> [Stage 2: Receiver] --λ--> Consumers
                  (n₁ servers, μ₁)   (D_link, p)  (n₂ servers, μ₂)
```

---

## Stage 1: Broker Queue (M/M/n₁)

### Equation T1: Stage 1 Utilization
```
ρ₁ = λ/(n₁·μ₁)
```

**where:**
- λ = arrival rate at broker (messages/sec)
- n₁ = number of broker threads
- μ₁ = broker service rate per thread (messages/sec/thread)

**Stability condition:** ρ₁ < 1

---

### Equation T2: Stage 1 Mean Waiting Time
```
W₁ = C(n₁, a₁) · (ρ₁/(1-ρ₁)) · (1/μ₁)
```

**where:**
- C(n₁, a₁) = Erlang-C probability (from M/M/N formulas)
- a₁ = λ/μ₁ = traffic intensity

---

### Equation T3: Stage 1 Mean Response Time
```
R₁ = W₁ + S₁ = W₁ + (1/μ₁)
```

---

## Network Layer

### Equation T4: Expected Network Time
```
E[Network Time] = (2 + p) · D_link
```

**Derivation:**
- Initial transmission: D_link (broker → receiver)
- ACK/NACK response: D_link (receiver → broker)
- Expected retries: p × (additional transmissions)

**Components:**
- `2·D_link` = baseline (send + ack)
- `p·D_link` = average retry overhead

**Examples:**
- p=0 (no failures): `2·D_link`
- p=0.2 (20% failures): `2.2·D_link` (10% higher)
- p=0.5 (50% failures): `2.5·D_link` (25% higher)

---

## Stage 2: Receiver Queue (M/M/n₂)

### **🔥 CRITICAL EQUATION T5: Stage 2 Effective Arrival Rate**
```
Λ₂ = λ/(1-p)
```

**This is the KEY insight of the tandem queue model!**

**Explanation:**
- Failed transmissions (probability p) are retried
- Each retry adds to the arrival stream at Stage 2
- Stage 2 sees MORE arrivals than Stage 1!

**Examples:**
- p=0: Λ₂ = λ (no retries)
- p=0.1: Λ₂ = 1.11λ (11% higher)
- p=0.2: Λ₂ = 1.25λ (25% higher)
- p=0.3: Λ₂ = 1.43λ (43% higher)

---

### Equation T6: Stage 2 Utilization
```
ρ₂ = Λ₂/(n₂·μ₂) = λ/((1-p)·n₂·μ₂)
```

**CRITICAL IMPLICATION:**
- If n₂ = n₁ and μ₂ = μ₁, then ρ₂ > ρ₁ when p > 0
- **Stage 2 is MORE loaded than Stage 1!**
- Stage 2 becomes the bottleneck!

**Stability condition:** ρ₂ < 1 → λ < (1-p)·n₂·μ₂

---

### Equation T7: Stage 2 Mean Waiting Time
```
W₂ = C(n₂, a₂) · (ρ₂/(1-ρ₂)) · (1/μ₂)
```

**where:**
- C(n₂, a₂) = Erlang-C for n₂ servers
- a₂ = Λ₂/μ₂ = **effective** traffic intensity

**Note:** Use Λ₂ (not λ) for Stage 2 calculations!

---

### Equation T8: Stage 2 Mean Response Time
```
R₂ = W₂ + S₂ = W₂ + (1/μ₂)
```

---

## End-to-End Latency

### Equation T9: Total Message Delivery Time
```
T_total = W₁ + S₁ + (2+p)·D_link + W₂ + S₂
```

**Breakdown:**
1. **Stage 1 queuing:** W₁
2. **Stage 1 service:** S₁ = 1/μ₁
3. **Network transmission:** (2+p)·D_link
4. **Stage 2 queuing:** W₂
5. **Stage 2 service:** S₂ = 1/μ₂

---

## Performance Metrics

### Equation T10: Stage 1 Queue Length
```
L₁ = λ · W₁
```
(Little's Law)

---

### Equation T11: Stage 2 Queue Length
```
L₂ = Λ₂ · W₂
```
(Little's Law with **effective** arrival rate Λ₂)

---

### Equation T12: System Throughput
```
X = λ  (in steady state, assuming stable system)
```

**Note:** Input rate = Output rate in steady state

---

## Key Insights

### Insight 1: Stage 2 Load Increase
```
Δρ = ρ₂ - ρ₁ = (λ/(n·μ)) · (1/(1-p) - 1) = (λ·p)/((n·μ)(1-p))
```

When p > 0, Stage 2 is always more loaded than Stage 1 (if n₁=n₂, μ₁=μ₂)!

---

### Insight 2: Bottleneck Condition
Stage 2 becomes bottleneck when:
```
ρ₂ > ρ₁
⟺ λ/((1-p)·n₂·μ₂) > λ/(n₁·μ₁)
⟺ n₁·μ₁ > (1-p)·n₂·μ₂
```

---

### Insight 3: Network Dominance
Network time dominates when:
```
(2+p)·D_link > W₁ + S₁ + W₂ + S₂
```

Typical for high-latency networks (e.g., D_link > 50ms)

---

## Example Calculation

**Given:**
- λ = 100 msg/sec
- n₁ = 10, μ₁ = 12 msg/sec/thread
- n₂ = 10, μ₂ = 12 msg/sec/thread
- D_link = 10ms = 0.01 sec
- p = 0.2 (20% failure rate)

**Calculate:**

1. **Stage 1 utilization:**
```
   ρ₁ = 100/(10×12) = 0.833
```

2. **Stage 2 effective arrival rate:**
```
   Λ₂ = 100/(1-0.2) = 125 msg/sec  (25% higher!)
```

3. **Stage 2 utilization:**
```
   ρ₂ = 125/(10×12) = 1.042  ⚠️ UNSTABLE!
```

4. **Solution:** Need more Stage 2 capacity!
   - Option 1: Increase n₂ to 11 → ρ₂ = 0.947 ✓
   - Option 2: Reduce p to 0.15 → Λ₂ = 117.6, ρ₂ = 0.980 ✓

---

## Implementation Notes

### Configuration Validation
Always check Stage 2 stability:
```python
Lambda2 = lambda_arrival / (1 - failure_prob)
rho2 = Lambda2 / (n2 * mu2)

if rho2 >= 1.0:
    raise ValueError("Stage 2 unstable!")
```

### Common Mistakes
❌ **Wrong:** Using λ for Stage 2 calculations
✅ **Correct:** Using Λ₂ = λ/(1-p) for Stage 2

❌ **Wrong:** Assuming ρ₁ = ρ₂ when n₁=n₂, μ₁=μ₂
✅ **Correct:** ρ₂ > ρ₁ when p > 0

---

## References

1. Li, J., Cui, Y., & Ma, Y. (2015). "Modeling Message Queueing Services with Reliability Guarantee in Cloud Computing Environment"
2. Kleinrock, L. (1975). "Queueing Systems, Volume 1: Theory"
3. Erlang-C formula and M/M/N theory
