/**
 * M/G/N vs M/M/N Comparison Page
 * Dedicated section as requested by professor
 * Compares heavy-tailed M/G/N against M/M/N baseline from Figures 11-15
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Slider,
  TextField,
  Button,
  Card,
  CardContent,
  Alert,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import Plot from 'react-plotly.js';
import { MathEquation } from '../components/MathEquation';
import axios from 'axios';

interface ComparisonMetrics {
  mmn: {
    mean_wait: number;
    mean_response: number;
    utilization: number;
    erlang_c: number;
  };
  mgn: {
    mean_wait: number;
    mean_response: number;
    coefficient_of_variation: number;
    variability_factor: number;
  };
}

export const MGNvsMMNComparison = () => {
  // Parameters
  const [lambda, setLambda] = useState(100); // Arrival rate
  const [mu, setMu] = useState(12); // Service rate
  const [N, setN] = useState(10); // Number of threads
  const [alpha, setAlpha] = useState(2.5); // Pareto shape parameter

  // Results
  const [metrics, setMetrics] = useState<ComparisonMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Calculate on mount and parameter change
  useEffect(() => {
    calculateComparison();
  }, [lambda, mu, N, alpha]);

  const calculateComparison = async () => {
    setLoading(true);
    setError(null);

    try {
      // Calculate M/M/N metrics
      const mmnResponse = await axios.post('/api/analytical/mmn', {
        arrival_rate: lambda,
        num_threads: N,
        service_rate: mu,
      });

      // Calculate M/G/N metrics (Pareto distribution)
      const meanService = 1 / mu;
      const cv2 = 1 / (alpha * (alpha - 2)); // C² = 1/(α(α-2))
      const variance = cv2 * meanService * meanService;

      const mgnResponse = await axios.post('/api/analytical/mgn', {
        arrival_rate: lambda,
        num_threads: N,
        mean_service: meanService,
        variance_service: variance,
      });

      setMetrics({
        mmn: mmnResponse.data.metrics,
        mgn: mgnResponse.data.metrics,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  // Calculate derived values
  const rho = lambda / (N * mu);
  const cv2 = alpha > 2 ? 1 / (alpha * (alpha - 2)) : Infinity;
  const scale = (1 / mu) * (alpha - 1) / alpha;

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 4, mb: 4, backgroundColor: 'primary.main', color: 'white' }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          M/G/N vs M/M/N Comparison
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.95 }}>
          Heavy-Tailed Workloads vs Exponential Baseline (Li et al. 2015, Figures 11-15)
        </Typography>
        <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Chip label={`λ = ${lambda} msg/sec`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`μ = ${mu} msg/sec`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`N = ${N} threads`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`α = ${alpha} (Pareto)`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`ρ = ${rho.toFixed(3)}`} color={rho < 1 ? 'success' : 'error'} sx={{ fontWeight: 'bold' }} />
        </Box>
      </Paper>

      {/* Mathematical Formulas */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom color="primary">
          Mathematical Formulas
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom color="primary">
                M/M/N Baseline (Exponential Service Times)
              </Typography>
              <Box sx={{ my: 2 }}>
                <MathEquation equation="\rho = \frac{\lambda}{N \cdot \mu}" />
                <MathEquation equation="C^2 = 1 \quad \text{(exponential)}" />
                <MathEquation equation="W_q = \frac{C(N,a) \cdot \rho}{N \cdot \mu \cdot (1-\rho)}" />
              </Box>
              <Typography variant="caption" color="text.secondary">
                C(N,a) = Erlang-C formula (Eq. 2)
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom color="secondary">
                M/G/N Heavy-Tailed (Pareto Service Times)
              </Typography>
              <Box sx={{ my: 2 }}>
                <MathEquation equation="f(t) = \frac{\alpha k^\alpha}{t^{\alpha+1}}, \quad t \geq k" />
                <MathEquation equation="C^2 = \frac{1}{\alpha(\alpha-2)}" />
                <MathEquation equation="W_q \approx W_q^{M/M/N} \cdot \frac{1 + C^2}{2}" />
              </Box>
              <Typography variant="caption" color="text.secondary">
                Pollaczek-Khinchin approximation (Eq. 10)
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Parameter Controls */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Interactive Parameters
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>Arrival Rate (λ): {lambda} msg/sec</Typography>
            <Slider
              value={lambda}
              onChange={(_, v) => setLambda(v as number)}
              min={10}
              max={200}
              step={10}
              marks
              valueLabelDisplay="auto"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>Service Rate (μ): {mu} msg/sec/thread</Typography>
            <Slider
              value={mu}
              onChange={(_, v) => setMu(v as number)}
              min={5}
              max={20}
              step={1}
              marks
              valueLabelDisplay="auto"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>Number of Threads (N): {N}</Typography>
            <Slider
              value={N}
              onChange={(_, v) => setN(v as number)}
              min={2}
              max={20}
              step={1}
              marks
              valueLabelDisplay="auto"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography gutterBottom component="div">
              Pareto Shape (α): {alpha}
              {alpha <= 2 && <Chip label="⚠ Infinite variance!" color="error" size="small" sx={{ ml: 1 }} />}
              {alpha > 2 && <Chip label={`C² = ${cv2.toFixed(2)}`} color="info" size="small" sx={{ ml: 1 }} />}
            </Typography>
            <Slider
              value={alpha}
              onChange={(_, v) => setAlpha(v as number)}
              min={2.1}
              max={5.0}
              step={0.1}
              marks={[
                { value: 2.1, label: '2.1 (Heavy)' },
                { value: 2.5, label: '2.5' },
                { value: 3.0, label: '3.0' },
                { value: 5.0, label: '5.0 (Light)' },
              ]}
              valueLabelDisplay="auto"
            />
          </Grid>
        </Grid>
        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
          <Button variant="contained" onClick={calculateComparison} disabled={loading}>
            {loading ? 'Calculating...' : 'Recalculate'}
          </Button>
          {rho >= 1 && (
            <Alert severity="error">
              System unstable! ρ = {rho.toFixed(3)} ≥ 1
            </Alert>
          )}
        </Box>
      </Paper>

      {/* Results Comparison */}
      {metrics && (
        <>
          <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              Comparative Results
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Metric</strong></TableCell>
                    <TableCell align="right"><strong>M/M/N (Baseline)</strong></TableCell>
                    <TableCell align="right"><strong>M/G/N (Heavy-Tailed)</strong></TableCell>
                    <TableCell align="right"><strong>Δ Increase</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Mean Waiting Time (Wq)</TableCell>
                    <TableCell align="right">{metrics.mmn.mean_wait.toFixed(6)} sec</TableCell>
                    <TableCell align="right">{metrics.mgn.mean_wait.toFixed(6)} sec</TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${((metrics.mgn.mean_wait / metrics.mmn.mean_wait - 1) * 100).toFixed(1)}%`}
                        color="error"
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Mean Response Time (R)</TableCell>
                    <TableCell align="right">{metrics.mmn.mean_response.toFixed(6)} sec</TableCell>
                    <TableCell align="right">{metrics.mgn.mean_response.toFixed(6)} sec</TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${((metrics.mgn.mean_response / metrics.mmn.mean_response - 1) * 100).toFixed(1)}%`}
                        color="warning"
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Coefficient of Variation (C²)</TableCell>
                    <TableCell align="right">1.000 (exponential)</TableCell>
                    <TableCell align="right">{metrics.mgn.coefficient_of_variation.toFixed(3)}</TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${((metrics.mgn.coefficient_of_variation - 1) * 100).toFixed(1)}%`}
                        color="info"
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {/* Visualization */}
          <Paper elevation={2} sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>
              Waiting Time Comparison
            </Typography>
            <Plot
              data={[
                {
                  x: ['M/M/N', 'M/G/N'],
                  y: [metrics.mmn.mean_wait, metrics.mgn.mean_wait],
                  type: 'bar',
                  marker: {
                    color: ['#1976d2', '#d32f2f'],
                  },
                  text: [
                    `${metrics.mmn.mean_wait.toFixed(6)} sec`,
                    `${metrics.mgn.mean_wait.toFixed(6)} sec`
                  ],
                  textposition: 'auto',
                },
              ]}
              layout={{
                title: { text: 'Mean Waiting Time: M/G/N vs M/M/N' },
                xaxis: { title: { text: 'Queue Model' } },
                yaxis: { title: { text: 'Mean Waiting Time (seconds)' } },
                width: 800,
                height: 400,
              }}
            />
          </Paper>
        </>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Container>
  );
};
