/**
 * API Service
 * Handles all communication with the FastAPI backend
 */

import axios, { AxiosInstance } from 'axios';
import type {
  MMNConfig,
  MGNConfig,
  TandemQueueConfig,
  SimulationResponse,
  SimulationStatus,
  SimulationResults,
  AnalyticalResponse,
  RaftRequest,
  VectorClockRequest,
  TwoPhaseCommitRequest,
  DistributedSimulationResponse,
} from '../types/models';

// Create axios instance with base configuration
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3100',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (for auth tokens, etc.)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    // const token = localStorage.getItem('auth_token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (for error handling)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Simulation Endpoints
// ============================================================================

export const simulationAPI = {
  /**
   * Run M/M/N simulation
   */
  runMMN: async (config: MMNConfig): Promise<SimulationResponse> => {
    const response = await api.post<SimulationResponse>('/api/simulations/mmn', config);
    return response.data;
  },

  /**
   * Run M/G/N simulation
   */
  runMGN: async (config: MGNConfig): Promise<SimulationResponse> => {
    const response = await api.post<SimulationResponse>('/api/simulations/mgn', config);
    return response.data;
  },

  /**
   * Run Tandem queue simulation
   */
  runTandem: async (config: TandemQueueConfig): Promise<SimulationResponse> => {
    const response = await api.post<SimulationResponse>('/api/simulations/tandem', config);
    return response.data;
  },

  /**
   * Get simulation status
   */
  getStatus: async (simulationId: string): Promise<SimulationStatus> => {
    const response = await api.get<SimulationStatus>(`/api/simulations/${simulationId}/status`);
    return response.data;
  },

  /**
   * Get simulation results
   */
  getResults: async (simulationId: string): Promise<SimulationResults> => {
    const response = await api.get<SimulationResults>(`/api/simulations/${simulationId}/results`);
    return response.data;
  },

  /**
   * Delete simulation
   */
  delete: async (simulationId: string): Promise<void> => {
    await api.delete(`/api/simulations/${simulationId}`);
  },

  /**
   * List all simulations
   */
  list: async (): Promise<any[]> => {
    const response = await api.get('/api/simulations/');
    return response.data;
  },
};

// ============================================================================
// Analytical Endpoints
// ============================================================================

export const analyticalAPI = {
  /**
   * Calculate M/M/N metrics analytically
   */
  calculateMMN: async (config: Pick<MMNConfig, 'arrival_rate' | 'num_threads' | 'service_rate'>): Promise<AnalyticalResponse> => {
    const response = await api.post<AnalyticalResponse>('/api/analytical/mmn', config);
    return response.data;
  },

  /**
   * Calculate M/G/N metrics analytically
   */
  calculateMGN: async (params: {
    arrival_rate: number;
    num_threads: number;
    mean_service: number;
    variance_service: number;
  }): Promise<AnalyticalResponse> => {
    const response = await api.post<AnalyticalResponse>('/api/analytical/mgn', params);
    return response.data;
  },

  /**
   * Calculate Tandem queue metrics analytically
   */
  calculateTandem: async (config: Omit<TandemQueueConfig, 'sim_duration' | 'warmup_time' | 'random_seed'>): Promise<AnalyticalResponse> => {
    const response = await api.post<AnalyticalResponse>('/api/analytical/tandem', config);
    return response.data;
  },

  /**
   * Get all analytical formulas
   */
  getFormulas: async (): Promise<any> => {
    const response = await api.get('/api/analytical/formulas');
    return response.data;
  },

  /**
   * Compare simulation vs analytical
   */
  compare: async (simulationResults: any, analyticalConfig: any): Promise<any> => {
    const response = await api.post('/api/analytical/compare', {
      simulation_results: simulationResults,
      analytical_config: analyticalConfig,
    });
    return response.data;
  },
};

// ============================================================================
// Distributed Systems Endpoints
// ============================================================================

export const distributedAPI = {
  /**
   * Run Raft consensus simulation
   */
  runRaft: async (request: RaftRequest): Promise<DistributedSimulationResponse> => {
    const response = await api.post<DistributedSimulationResponse>('/api/distributed/raft', request);
    return response.data;
  },

  /**
   * Run Vector Clocks simulation
   */
  runVectorClocks: async (request: VectorClockRequest): Promise<DistributedSimulationResponse> => {
    const response = await api.post<DistributedSimulationResponse>('/api/distributed/vector-clocks', request);
    return response.data;
  },

  /**
   * Run Two-Phase Commit simulation
   */
  run2PC: async (request: TwoPhaseCommitRequest): Promise<DistributedSimulationResponse> => {
    const response = await api.post<DistributedSimulationResponse>('/api/distributed/two-phase-commit', request);
    return response.data;
  },

  /**
   * List available protocols
   */
  listProtocols: async (): Promise<any> => {
    const response = await api.get('/api/distributed/protocols');
    return response.data;
  },
};

// ============================================================================
// Results Endpoints
// ============================================================================

export const resultsAPI = {
  /**
   * List results with filtering
   */
  list: async (params?: {
    model_type?: string;
    status?: string;
    limit?: number;
  }): Promise<any> => {
    const response = await api.get('/api/results/', { params });
    return response.data;
  },

  /**
   * Get specific result
   */
  get: async (simulationId: string): Promise<any> => {
    const response = await api.get(`/api/results/${simulationId}`);
    return response.data;
  },

  /**
   * Export result
   */
  export: async (simulationId: string, format: 'json' | 'csv'): Promise<Blob> => {
    const response = await api.get(`/api/results/${simulationId}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Delete result
   */
  delete: async (simulationId: string): Promise<void> => {
    await api.delete(`/api/results/${simulationId}`);
  },

  /**
   * Compare multiple results
   */
  compare: async (simulationIds: string[]): Promise<any> => {
    const response = await api.post('/api/results/compare', simulationIds);
    return response.data;
  },
};

// ============================================================================
// Health Check
// ============================================================================

export const healthCheck = async (): Promise<any> => {
  const response = await api.get('/api/health');
  return response.data;
};

// Export the axios instance for advanced use
export default api;
