/**
 * Results Viewer - View simulation results
 */

import { Container, Typography, Paper } from '@mui/material';

export const ResultsViewer = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, backgroundColor: 'success.main', color: 'white' }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          Results Viewer
        </Typography>
        <Typography variant="h6">
          Browse and analyze simulation results
        </Typography>
      </Paper>
    </Container>
  );
};
