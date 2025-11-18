/**
 * M/M/N Calculator - Interactive analytical calculator
 * Real-time parameter adjustment with instant results
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Slider,
  Card,
  CardContent,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import Plot from 'react-plotly.js';
import { MathEquation, Equation1, Equation2, Equation4, Equation5 } from '../components/MathEquation';
import axios from 'axios';

interface MMNMetrics {
  utilization: number;
  erlang_c: number;
  mean_wait: number;
  mean_response: number;
  mean_queue_length: number;
  mean_system_size: number;
}

export const MMNCalculator = () => {
  // Parameters
  const [lambda, setLambda] = useState(100);
  const [mu, setMu] = useState(12);
  const [N, setN] = useState(10);

  // Results
  const [metrics, setMetrics] = useState<MMNMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-calculate on parameter change
  useEffect(() => {
    calculate();
  }, [lambda, mu, N]);

  const calculate = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/analytical/mmn', {
        arrival_rate: lambda,
        num_threads: N,
        service_rate: mu,
      });

      setMetrics(response.data.metrics);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const rho = lambda / (N * mu);
  const a = lambda / mu;

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 4, mb: 4, backgroundColor: 'primary.main', color: 'white' }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          M/M/N Queue Calculator
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.95 }}>
          Instant Analytical Results - No Simulation Required
        </Typography>
        <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Chip label={`λ = ${lambda} msg/sec`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`μ = ${mu} msg/sec/thread`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`N = ${N} threads`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`ρ = ${rho.toFixed(3)}`} color={rho < 1 ? 'success' : 'error'} sx={{ fontWeight: 'bold' }} />
        </Box>
      </Paper>

      {/* Parameters */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom color="primary">
          Parameters
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Typography gutterBottom fontWeight="bold">
              Arrival Rate (λ): {lambda} msg/sec
            </Typography>
            <Slider
              value={lambda}
              onChange={(_, v) => setLambda(v as number)}
              min={10}
              max={200}
              step={5}
              marks={[
                { value: 10, label: '10' },
                { value: 100, label: '100' },
                { value: 200, label: '200' },
              ]}
              valueLabelDisplay="auto"
            />
            <Typography variant="caption" color="text.secondary">
              Rate of incoming requests
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography gutterBottom fontWeight="bold">
              Service Rate (μ): {mu} msg/sec/thread
            </Typography>
            <Slider
              value={mu}
              onChange={(_, v) => setMu(v as number)}
              min={5}
              max={25}
              step={1}
              marks={[
                { value: 5, label: '5' },
                { value: 15, label: '15' },
                { value: 25, label: '25' },
              ]}
              valueLabelDisplay="auto"
            />
            <Typography variant="caption" color="text.secondary">
              Processing rate per thread
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography gutterBottom fontWeight="bold">
              Number of Threads (N): {N}
            </Typography>
            <Slider
              value={N}
              onChange={(_, v) => setN(v as number)}
              min={1}
              max={30}
              step={1}
              marks={[
                { value: 1, label: '1' },
                { value: 15, label: '15' },
                { value: 30, label: '30' },
              ]}
              valueLabelDisplay="auto"
            />
            <Typography variant="caption" color="text.secondary">
              Server capacity
            </Typography>
          </Grid>
        </Grid>

        {rho >= 1 && (
          <Alert severity="error" sx={{ mt: 2 }}>
            System is UNSTABLE! ρ = {rho.toFixed(3)} ≥ 1. Queue will grow without bound.
            Increase N or μ, or decrease λ.
          </Alert>
        )}
      </Paper>

      {/* Formulas */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom color="primary">
          M/M/N Formulas
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Equation1 />
          </Grid>
          <Grid item xs={12} md={6}>
            <Equation2 />
          </Grid>
          <Grid item xs={12} md={6}>
            <Equation4 />
          </Grid>
          <Grid item xs={12} md={6}>
            <Equation5 />
          </Grid>
        </Grid>
      </Paper>

      {/* Results */}
      {metrics && (
        <>
          <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
            <Typography variant="h5" gutterBottom color="primary">
              Results
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={4}>
                <Card sx={{ height: '100%', bgcolor: 'primary.light' }}>
                  <CardContent>
                    <Typography color="primary.dark" gutterBottom>
                      Utilization (ρ)
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {(metrics.utilization * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {metrics.utilization < 0.7 ? 'Low load' : metrics.utilization < 0.9 ? 'Moderate load' : 'High load'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Card sx={{ height: '100%', bgcolor: 'secondary.light' }}>
                  <CardContent>
                    <Typography color="secondary.dark" gutterBottom>
                      Erlang-C (C)
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {(metrics.erlang_c * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Probability of queueing
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Card sx={{ height: '100%', bgcolor: 'success.light' }}>
                  <CardContent>
                    <Typography color="success.dark" gutterBottom>
                      Mean Wait (Wq)
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {(metrics.mean_wait * 1000).toFixed(2)}ms
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Time in queue
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Card sx={{ height: '100%', bgcolor: 'warning.light' }}>
                  <CardContent>
                    <Typography color="warning.dark" gutterBottom>
                      Mean Response (R)
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {(metrics.mean_response * 1000).toFixed(2)}ms
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Total time (wait + service)
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Card sx={{ height: '100%', bgcolor: 'error.light' }}>
                  <CardContent>
                    <Typography color="error.dark" gutterBottom>
                      Queue Length (Lq)
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {metrics.mean_queue_length.toFixed(2)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Avg customers waiting
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Card sx={{ height: '100%', bgcolor: 'info.light' }}>
                  <CardContent>
                    <Typography color="info.dark" gutterBottom>
                      System Size (L)
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {metrics.mean_system_size.toFixed(2)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Avg customers in system
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>

          {/* Visualization */}
          <Paper elevation={2} sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom color="primary">
              Performance Visualization
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Plot
                  data={[
                    {
                      type: 'indicator',
                      mode: 'gauge+number+delta',
                      value: metrics.utilization * 100,
                      title: { text: 'Utilization (%)' },
                      delta: { reference: 80 },
                      gauge: {
                        axis: { range: [0, 100] },
                        bar: { color: metrics.utilization < 0.7 ? 'green' : metrics.utilization < 0.9 ? 'orange' : 'red' },
                        steps: [
                          { range: [0, 70], color: 'lightgreen' },
                          { range: [70, 90], color: 'lightyellow' },
                          { range: [90, 100], color: 'lightcoral' },
                        ],
                        threshold: {
                          line: { color: 'red', width: 4 },
                          thickness: 0.75,
                          value: 95,
                        },
                      },
                    },
                  ]}
                  layout={{
                    width: 400,
                    height: 300,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Plot
                  data={[
                    {
                      labels: ['Service Time', 'Queue Wait'],
                      values: [1 / mu, metrics.mean_wait],
                      type: 'pie',
                      marker: {
                        colors: ['#2196f3', '#f44336'],
                      },
                    },
                  ]}
                  layout={{
                    title: { text: 'Response Time Breakdown' },
                    width: 400,
                    height: 300,
                  }}
                />
              </Grid>
            </Grid>
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
