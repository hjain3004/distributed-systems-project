/**
 * Main Application Component
 * Now with API connection testing
 */

import { ThemeProvider, CssBaseline } from '@mui/material';
import { Box, Container, Typography, Paper } from '@mui/material';
import { theme } from './utils/theme';
import { ApiTest } from './components/ApiTest';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          backgroundColor: 'background.default',
          py: 4,
        }}
      >
        <Container maxWidth="lg">
          <Paper
            elevation={3}
            sx={{
              p: 4,
              textAlign: 'center',
              mb: 3,
            }}
          >
            <Typography variant="h2" gutterBottom color="primary">
              Distributed Systems Performance Modeling
            </Typography>
            <Typography variant="h5" color="text.secondary" gutterBottom>
              Interactive Web Platform
            </Typography>
            <Typography variant="body1" sx={{ mt: 2 }}>
              ✅ React + TypeScript + Vite
            </Typography>
            <Typography variant="body1">
              ✅ Material-UI Theme
            </Typography>
            <Typography variant="body1">
              ✅ Backend API Connected!
            </Typography>
          </Paper>

          {/* API Connection Test */}
          <ApiTest />
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
