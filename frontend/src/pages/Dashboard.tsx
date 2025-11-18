/**
 * Dashboard - Main landing page with project overview
 */

import { Box, Container, Typography, Paper, Grid, Card, CardContent } from '@mui/material';
import { Calculate, CompareArrows, Analytics, Science } from '@mui/icons-material';

export const Dashboard = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Paper
        elevation={3}
        sx={{
          p: 6,
          mb: 4,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          textAlign: 'center',
        }}
      >
        <Typography variant="h2" gutterBottom fontWeight="bold">
          Distributed Systems Performance Modeling
        </Typography>
        <Typography variant="h5" sx={{ mb: 2, opacity: 0.95 }}>
          Heavy-Tailed Workload Analysis with M/M/N and M/G/N Queueing Models
        </Typography>
        <Typography variant="body1" sx={{ opacity: 0.9 }}>
          Based on Li et al. (2015) | 15 Analytical Equations | Interactive Visualizations
        </Typography>
      </Paper>

      {/* Key Features Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: '100%', transition: '0.3s', '&:hover': { transform: 'translateY(-4px)', boxShadow: 6 } }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Calculate sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                15 Analytical Equations
              </Typography>
              <Typography variant="body2" color="text.secondary">
                M/M/N baseline (Eq. 1-5), M/G/N heavy-tailed (Eq. 6-10), Threading models (Eq. 11-15)
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: '100%', transition: '0.3s', '&:hover': { transform: 'translateY(-4px)', boxShadow: 6 } }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <CompareArrows sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                M/G/N vs M/M/N
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Dedicated comparison section validating against Figures 11-15 from Li et al. (2015)
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: '100%', transition: '0.3s', '&:hover': { transform: 'translateY(-4px)', boxShadow: 6 } }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Analytics sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Heavy-Tailed Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pareto, Lognormal, Weibull distributions with coefficient of variation C² analysis
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: '100%', transition: '0.3s', '&:hover': { transform: 'translateY(-4px)', boxShadow: 6 } }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Science sx={{ fontSize: 60, color: 'error.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Tandem Queues
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Two-stage broker→receiver model with Λ₂ = λ/(1-p) validation
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Mathematical Foundation */}
      <Paper elevation={2} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom color="primary">
          Mathematical Foundation
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom>
                M/M/N Baseline (Equations 1-5)
              </Typography>
              <Typography variant="body2" component="div">
                • Eq. 1: Utilization ρ = λ/(N·μ)<br />
                • Eq. 2: Erlang-C formula<br />
                • Eq. 3: P₀ (system empty)<br />
                • Eq. 4: Mean queue length Lq<br />
                • Eq. 5: Mean waiting time Wq
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom>
                M/G/N Heavy-Tailed (Equations 6-10)
              </Typography>
              <Typography variant="body2" component="div">
                • Eq. 6: Pareto PDF f(t)<br />
                • Eq. 7: Mean E[S]<br />
                • Eq. 8: Second moment E[S²]<br />
                • Eq. 9: Coefficient of variation C²<br />
                • Eq. 10: Approximated Wq
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom>
                Threading Models (Equations 11-15)
              </Typography>
              <Typography variant="body2" component="div">
                • Eq. 11: Max connections<br />
                • Eq. 12: Throughput<br />
                • Eq. 13: Effective service rate<br />
                • Eq. 14: Thread saturation<br />
                • Eq. 15: P99 latency
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};
