/**
 * API Connection Test Component
 * Tests backend connectivity and displays status
 */

import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import { healthCheck, simulationAPI } from '../services/api';

export const ApiTest = () => {
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [mockResult, setMockResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Test health endpoint on mount
  useEffect(() => {
    testHealth();
  }, []);

  const testHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await healthCheck();
      setHealthStatus(result);
    } catch (err: any) {
      setError(`Health check failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testMockSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await simulationAPI.runMMN({
        arrival_rate: 100,
        num_threads: 10,
        service_rate: 12,
        sim_duration: 1000,
        warmup_time: 100,
        random_seed: 42,
      });
      setMockResult(result);
    } catch (err: any) {
      setError(`Simulation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          API Connection Test
        </Typography>

        <Box sx={{ my: 2 }}>
          {loading && <CircularProgress size={24} />}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {healthStatus && (
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Status:</strong> {healthStatus.status}
              </Typography>
              <Typography variant="body2">
                <strong>Service:</strong> {healthStatus.service}
              </Typography>
              <Typography variant="body2">
                <strong>Message:</strong> {healthStatus.message}
              </Typography>
            </Alert>
          )}

          {mockResult && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Simulation ID:</strong> {mockResult.simulation_id}
              </Typography>
              <Typography variant="body2">
                <strong>Status:</strong> {mockResult.status}
              </Typography>
              <Typography variant="body2">
                <strong>Model:</strong> {mockResult.model_type}
              </Typography>
              <Typography variant="body2">
                <strong>Mean Wait:</strong> {mockResult.metrics?.mean_wait}s
              </Typography>
              <Typography variant="body2">
                <strong>Utilization:</strong> {mockResult.metrics?.utilization}
              </Typography>
            </Alert>
          )}
        </Box>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            onClick={testHealth}
            disabled={loading}
          >
            Test Health
          </Button>

          <Button
            variant="contained"
            color="secondary"
            onClick={testMockSimulation}
            disabled={loading}
          >
            Test Simulation
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};
