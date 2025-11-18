/**
 * Tandem Queue - Two-Stage Model
 */

import { Container, Typography, Paper, Box } from '@mui/material';
import { TandemEquation1, TandemEquation2, TandemEquation3 } from '../components/MathEquation';

export const TandemQueue = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, backgroundColor: 'info.main', color: 'white' }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          Tandem Queue Model
        </Typography>
        <Typography variant="h6">
          Two-Stage Broker→Receiver Architecture (Li et al. 2015)
        </Typography>
      </Paper>
      <Paper elevation={2} sx={{ p: 4, mt: 3 }}>
        <Typography variant="h5" gutterBottom color="primary">
          Critical Equations
        </Typography>
        <TandemEquation1 />
        <TandemEquation2 />
        <TandemEquation3 />
      </Paper>
    </Container>
  );
};
