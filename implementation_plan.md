# Implementation Plan: Refined Tandem Queue Analytical Model

## Goal
Improve the accuracy of the Tandem Queue analytical model for heavy-tailed workloads by implementing Whitt's Queueing Network Analyzer (QNA) approximations. This addresses the theoretical pitfall of assuming independent Poisson arrivals at Stage 2.

## User Review Required
> [!IMPORTANT]
> This change introduces an **approximation** (Whitt's QNA) to replace the previous "exact" but incorrect M/M/n assumption for Stage 2. The results will no longer match M/M/n formulas but should better match the heavy-tailed simulation.

## Proposed Changes

### `src/analysis/analytical.py`

#### [MODIFY] `TandemQueueAnalytical` class

1.  **Add `stage1_output_variability()` method:**
    *   Implement Whitt's approximation for M/G/m output variability:
        $$C_{d}^2 = 1 + \frac{\rho^2}{\sqrt{m}}(C_s^2 - 1)$$
    *   Where $C_s^2$ is the coefficient of variation of Stage 1 service time.

2.  **Update `stage2_waiting_time()` method:**
    *   Calculate $C_{a,2}^2$ (Stage 2 arrival variability) using Stage 1 output variability.
        *   Note: We must also account for the network delay and random failures (splitting/merging), but for a first-order approximation, we can assume $C_{a,2}^2 \approx C_{d,1}^2$.
    *   Use the **Allen-Cunneen approximation** for Stage 2 waiting time:
        $$W_{q,2} \approx W_{M/M/n} \cdot \frac{C_{a,2}^2 + C_{s,2}^2}{2}$$
    *   This replaces the current call to `self.stage2_model.mean_waiting_time()` which assumes $C_{a,2}^2 = 1$.

3.  **Update `__init__`:**
    *   Accept `config` object or specific distribution parameters ($C_s^2$) to calculate variabilities. Currently it only takes rates. I will add optional arguments for $C_{s,1}^2$ and $C_{s,2}^2$ (defaulting to 1.0 for exponential).

## Verification Plan

### Automated Tests
1.  **Run `experiments/heavy_tail_tandem.py`:**
    *   Compare the new analytical prediction with the simulation results.
    *   Expectation: The analytical model should now predict higher wait times for Stage 2, closing the gap with the simulation (or at least moving in the right direction).

2.  **Unit Tests:**
    *   Add a test case in `tests/test_analytical.py` (if exists) or a new script to verify the QNA formula implementation.

### Manual Verification
*   Inspect the output of `heavy_tail_tandem.py` to ensure the "Difference" percentage decreases or is theoretically explainable.
