/**
 * M/G/N Calculator - Heavy-Tailed Distributions
 * Interactive calculator with Pareto, Lognormal, and Weibull distributions
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
} from '@mui/material';
import Plot from 'react-plotly.js';
import { MathEquation, Equation6, Equation7, Equation9, Equation10 } from '../components/MathEquation';
import axios from 'axios';

interface MGNMetrics {
  mean_wait: number;
  mean_response: number;
  coefficient_of_variation: number;
  variability_factor: number;
}

export const MGNCalculator = () => {
  // Parameters
  const [lambda, setLambda] = useState(100);
  const [mu, setMu] = useState(12);
  const [N, setN] = useState(10);
  const [alpha, setAlpha] = useState(2.5); // Pareto shape parameter
  const [distribution, setDistribution] = useState<'pareto' | 'lognormal' | 'weibull'>('pareto');

  // Results
  const [metrics, setMetrics] = useState<MGNMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-calculate on parameter change
  useEffect(() => {
    calculate();
  }, [lambda, mu, N, alpha, distribution]);

  const calculate = async () => {
    setLoading(true);
    setError(null);

    try {
      const meanService = 1 / mu;
      const cv2 = alpha > 2 ? 1 / (alpha * (alpha - 2)) : 10; // C² = 1/(α(α-2))
      const variance = cv2 * meanService * meanService;

      const response = await axios.post('/api/analytical/mgn', {
        arrival_rate: lambda,
        num_threads: N,
        mean_service: meanService,
        variance_service: variance,
      });

      setMetrics(response.data.metrics);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const rho = lambda / (N * mu);
  const meanService = 1 / mu;
  const cv2 = alpha > 2 ? 1 / (alpha * (alpha - 2)) : Infinity;
  const scale = meanService * (alpha - 1) / alpha;

  // Generate distribution comparison data
  const generateDistributionData = () => {
    const t = Array.from({ length: 100 }, (_, i) => (i + 1) * 0.001);

    // Exponential (M/M/N baseline)
    const exponential = t.map(x => mu * Math.exp(-mu * x));

    // Pareto (heavy-tailed)
    const pareto = t.map(x => {
      if (x < scale) return 0;
      return (alpha * Math.pow(scale, alpha)) / Math.pow(x, alpha + 1);
    });

    return { t, exponential, pareto };
  };

  const distData = generateDistributionData();

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 4, mb: 4, backgroundColor: 'secondary.main', color: 'white' }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          M/G/N Queue Calculator (Heavy-Tailed)
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.95 }}>
          Pareto, Lognormal, and Weibull Distributions - Analytical Results
        </Typography>
        <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Chip label={`λ = ${lambda} msg/sec`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`μ = ${mu} msg/sec/thread`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`N = ${N} threads`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`α = ${alpha}`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
          <Chip label={`ρ = ${rho.toFixed(3)}`} color={rho < 1 ? 'success' : 'error'} sx={{ fontWeight: 'bold' }} />
          <Chip label={`C² = ${cv2.toFixed(2)}`} sx={{ bgcolor: 'white', fontWeight: 'bold' }} />
        </Box>
      </Paper>

      {/* Parameters */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom color="secondary">
          Parameters
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
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
          </Grid>
          <Grid item xs={12} md={6}>
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
          </Grid>
          <Grid item xs={12} md={6}>
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
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography gutterBottom fontWeight="bold" component="div">
              Pareto Shape (α): {alpha}
              {alpha <= 2 && <Chip label="⚠ Infinite variance!" color="error" size="small" sx={{ ml: 1 }} />}
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
          {/* Distribution Type Selector */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Distribution Type</InputLabel>
              <Select
                value={distribution}
                label="Distribution Type"
                onChange={(e) => setDistribution(e.target.value as 'pareto' | 'lognormal' | 'weibull')}
              >
                <MenuItem value="pareto">Pareto (Heavy-Tailed)</MenuItem>
                <MenuItem value="lognormal">Lognormal</MenuItem>
                <MenuItem value="weibull">Weibull</MenuItem>
              </Select>
            </FormControl>
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
        <Typography variant="h5" gutterBottom color="secondary">
          M/G/N Heavy-Tailed Formulas
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Equation6 />
          </Grid>
          <Grid item xs={12} md={6}>
            <Equation7 />
          </Grid>
          <Grid item xs={12} md={6}>
            <Equation9 />
          </Grid>
          <Grid item xs={12} md={6}>
            <Equation10 />
          </Grid>
        </Grid>
      </Paper>

      {/* Distribution Visualization */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom color="secondary">
          Service Time Distribution Comparison
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Comparing Exponential (M/M/N) vs Pareto (M/G/N) service time distributions.
          Notice the heavy tail in Pareto - rare but extremely long service times.
        </Typography>
        <Plot
          data={[
            {
              x: distData.t,
              y: distData.exponential,
              type: 'scatter',
              mode: 'lines',
              name: 'Exponential (C² = 1)',
              line: { color: '#1976d2', width: 3 },
            },
            {
              x: distData.t,
              y: distData.pareto,
              type: 'scatter',
              mode: 'lines',
              name: `Pareto (α = ${alpha}, C² = ${cv2.toFixed(2)})`,
              line: { color: '#d32f2f', width: 3, dash: 'dash' },
            },
          ]}
          layout={{
            title: { text: 'Service Time Probability Density Functions' },
            xaxis: { title: { text: 'Service Time (seconds)' }, type: 'log' },
            yaxis: { title: { text: 'Probability Density' }, type: 'log' },
            width: 900,
            height: 500,
            showlegend: true,
            legend: { x: 0.7, y: 0.95 },
          }}
        />
      </Paper>

      {/* Results */}
      {metrics && (
        <>
          <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
            <Typography variant="h5" gutterBottom color="secondary">
              Performance Metrics
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%', bgcolor: 'secondary.light' }}>
                  <CardContent>
                    <Typography color="secondary.dark" gutterBottom>
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
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%', bgcolor: 'warning.light' }}>
                  <CardContent>
                    <Typography color="warning.dark" gutterBottom>
                      Mean Response (R)
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {(metrics.mean_response * 1000).toFixed(2)}ms
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Total time
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%', bgcolor: 'info.light' }}>
                  <CardContent>
                    <Typography color="info.dark" gutterBottom>
                      CV² (Variability)
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {metrics.coefficient_of_variation.toFixed(2)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {metrics.coefficient_of_variation > 1 ? 'High variance' : 'Low variance'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%', bgcolor: 'error.light' }}>
                  <CardContent>
                    <Typography color="error.dark" gutterBottom>
                      Variability Impact
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {metrics.variability_factor.toFixed(2)}x
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      (1 + C²) / 2
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>

          {/* Visualizations */}
          <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
            <Typography variant="h5" gutterBottom color="secondary">
              Impact Visualization
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Plot
                  data={[
                    {
                      type: 'indicator',
                      mode: 'number+delta',
                      value: metrics.coefficient_of_variation,
                      title: { text: 'Coefficient of Variation (C²)' },
                      delta: { reference: 1, valueformat: '.2f' },
                      number: { valueformat: '.2f' },
                    },
                  ]}
                  layout={{
                    width: 400,
                    height: 250,
                  }}
                />
                <Typography variant="caption" color="text.secondary" align="center" display="block">
                  C² = 1 for exponential (M/M/N baseline)
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Plot
                  data={[
                    {
                      labels: ['Base Delay', 'Variability Penalty'],
                      values: [1, metrics.variability_factor - 1],
                      type: 'pie',
                      marker: {
                        colors: ['#2196f3', '#f44336'],
                      },
                      textinfo: 'label+percent',
                    },
                  ]}
                  layout={{
                    title: { text: 'Waiting Time Composition' },
                    width: 400,
                    height: 300,
                  }}
                />
              </Grid>
            </Grid>
          </Paper>

          {/* Alpha Impact Analysis */}
          <Paper elevation={2} sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom color="secondary">
              Pareto Shape Parameter (α) Impact
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Lower α values mean heavier tails (more extreme outliers). This dramatically increases waiting times.
            </Typography>
            <Plot
              data={[
                {
                  x: [2.1, 2.3, 2.5, 2.7, 3.0, 3.5, 4.0, 5.0],
                  y: [2.1, 2.3, 2.5, 2.7, 3.0, 3.5, 4.0, 5.0].map(a => 1 / (a * (a - 2))),
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'C² = 1 / (α(α-2))',
                  line: { color: '#d32f2f', width: 3 },
                  marker: { size: 10 },
                },
              ]}
              layout={{
                title: { text: 'Coefficient of Variation vs Pareto Shape' },
                xaxis: { title: { text: 'Pareto Shape (α)' } },
                yaxis: { title: { text: 'Coefficient of Variation (C²)' }, type: 'log' },
                width: 900,
                height: 400,
                annotations: [
                  {
                    x: alpha,
                    y: cv2,
                    text: `Current: α=${alpha}, C²=${cv2.toFixed(2)}`,
                    showarrow: true,
                    arrowhead: 2,
                    ax: 40,
                    ay: -40,
                  },
                ],
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
