/**
 * All 15 Equations Page
 * Comprehensive display of all analytical formulas
 */

import { Container, Typography, Paper, Grid, Box, Divider, Chip } from '@mui/material';
import {
  Equation1,
  Equation2,
  Equation3,
  Equation4,
  Equation5,
  Equation6,
  Equation7,
  Equation8,
  Equation9,
  Equation10,
  Equation11,
  Equation12,
  Equation13,
  Equation14,
  Equation15,
  TandemEquation1,
  TandemEquation2,
  TandemEquation3,
  TandemEquation4,
  TandemEquation5,
} from '../components/MathEquation';

export const AllEquations = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 4, mb: 4, backgroundColor: 'primary.main', color: 'white' }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          15 Core Analytical Equations
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.95 }}>
          Complete Mathematical Framework for Queue Modeling
        </Typography>
      </Paper>

      {/* Section 1: M/M/N Baseline (Equations 1-5) */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" color="primary" fontWeight="bold">
            Section 1: M/M/N Baseline
          </Typography>
          <Chip label="Equations 1-5" color="primary" sx={{ ml: 2 }} />
        </Box>
        <Typography variant="body1" paragraph color="text.secondary">
          Exponential service times (C² = 1). Forms the baseline for comparison.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation1 />
              <Typography variant="caption" color="text.secondary">
                System utilization. Must be &lt; 1 for stability.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation2 />
              <Typography variant="caption" color="text.secondary">
                Probability that arriving customer must wait (queue not empty).
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation3 />
              <Typography variant="caption" color="text.secondary">
                Probability system is empty (all servers idle).
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation4 />
              <Typography variant="caption" color="text.secondary">
                Average number of customers waiting in queue.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation5 />
              <Typography variant="caption" color="text.secondary">
                Average time spent waiting in queue (Little's Law).
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Section 2: M/G/N Heavy-Tailed (Equations 6-10) */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" color="secondary" fontWeight="bold">
            Section 2: M/G/N Heavy-Tailed Extension
          </Typography>
          <Chip label="Equations 6-10" color="secondary" sx={{ ml: 2 }} />
        </Box>
        <Typography variant="body1" paragraph color="text.secondary">
          Pareto distribution for heavy-tailed service times (C² &gt; 1). Models real-world workloads.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation6 />
              <Typography variant="caption" color="text.secondary">
                Pareto probability density function. α controls tail heaviness (α &lt; 2 = infinite variance!).
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation7 />
              <Typography variant="caption" color="text.secondary">
                Mean service time. Requires α &gt; 1.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation8 />
              <Typography variant="caption" color="text.secondary">
                Second moment. Requires α &gt; 2.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation9 />
              <Typography variant="caption" color="text.secondary">
                Coefficient of variation (CORRECTED). α=2.5 → C²=1.0.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation10 />
              <Typography variant="caption" color="text.secondary">
                Pollaczek-Khinchin approximation for M/G/N waiting time.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Section 3: Threading Models (Equations 11-15) */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" color="success.main" fontWeight="bold">
            Section 3: Threading Models
          </Typography>
          <Chip label="Equations 11-15" color="success" sx={{ ml: 2 }} />
        </Box>
        <Typography variant="body1" paragraph color="text.secondary">
          Dedicated vs shared thread pools. Overhead and saturation effects.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation11 />
              <Typography variant="caption" color="text.secondary">
                Maximum concurrent connections in dedicated threading.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation12 />
              <Typography variant="caption" color="text.secondary">
                System throughput (limited by threads or arrivals).
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation13 />
              <Typography variant="caption" color="text.secondary">
                Effective service rate with thread contention overhead.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation14 />
              <Typography variant="caption" color="text.secondary">
                Probability all threads are busy (saturation).
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Equation15 />
              <Typography variant="caption" color="text.secondary">
                99th percentile latency (assumes normal distribution - fails for heavy tails!).
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Bonus: Tandem Queue Equations */}
      <Paper elevation={2} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" color="info.main" fontWeight="bold">
            Bonus: Tandem Queue Model
          </Typography>
          <Chip label="Li et al. 2015" color="info" sx={{ ml: 2 }} />
        </Box>
        <Typography variant="body1" paragraph color="text.secondary">
          Two-stage broker→receiver architecture. Critical insight: Λ₂ = λ/(1-p).
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <TandemEquation1 />
              <Typography variant="caption" color="text.secondary">
                Stage 1 (broker) utilization.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <TandemEquation2 />
              <Typography variant="caption" color="text.secondary">
                Stage 2 sees HIGHER arrival rate due to retransmissions!
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <TandemEquation3 />
              <Typography variant="caption" color="text.secondary">
                Stage 2 utilization (must account for retries).
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <TandemEquation4 />
              <Typography variant="caption" color="text.secondary">
                Expected network time (send + ACK + retries).
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <TandemEquation5 />
              <Typography variant="caption" color="text.secondary">
                End-to-end latency through both stages and network.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};
