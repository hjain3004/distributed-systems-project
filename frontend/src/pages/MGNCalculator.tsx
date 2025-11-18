/**
 * M/G/N Calculator - Heavy-Tailed Distributions
 */

import { Container, Typography, Paper, Box } from '@mui/material';

export const MGNCalculator = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, backgroundColor: 'secondary.main', color: 'white' }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          M/G/N Calculator (Heavy-Tailed)
        </Typography>
        <Typography variant="h6">
          Pareto, Lognormal, and Weibull Distributions
        </Typography>
      </Paper>
      <Box sx={{ mt: 3 }}>
        <Typography variant="body1">
          📊 Interactive M/G/N calculator with Pareto distributions will be available here.
          Use the M/G/N vs M/M/N Comparison page for now.
        </Typography>
      </Box>
    </Container>
  );
};
