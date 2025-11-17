/**
 * TypeScript Type Definitions
 * Mirrors the backend Pydantic models
 */

// ============================================================================
// Simulation Models
// ============================================================================

export interface MMNConfig {
  arrival_rate: number;
  num_threads: number;
  service_rate: number;
  sim_duration: number;
  warmup_time: number;
  random_seed?: number;
}

export interface MGNConfig extends MMNConfig {
  distribution: 'pareto' | 'lognormal' | 'exponential';
  alpha: number;
}

export interface TandemQueueConfig {
  arrival_rate: number;
  n1: number;
  mu1: number;
  n2: number;
  mu2: number;
  network_delay: number;
  failure_prob: number;
  sim_duration: number;
  warmup_time: number;
  random_seed?: number;
}

export type QueueModelType = 'M/M/N' | 'M/G/N' | 'Tandem' | 'Priority' | 'Finite Capacity';

export interface SimulationResponse {
  simulation_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  model_type: QueueModelType;
  message: string;
  created_at: string;
}

export interface SimulationStatus {
  simulation_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  started_at: string;
  completed_at?: string;
}

export interface SimulationMetrics {
  mean_wait: number;
  mean_service: number;
  mean_response: number;
  mean_queue_length: number;
  p50_wait: number;
  p95_wait: number;
  p99_wait: number;
  p50_response: number;
  p95_response: number;
  p99_response: number;
  utilization: number;
  total_messages?: number;
}

export interface SimulationResults {
  simulation_id: string;
  model_type: QueueModelType;
  config: MMNConfig | MGNConfig | TandemQueueConfig;
  results: any;
  metrics: SimulationMetrics;
  completed_at: string;
}

// ============================================================================
// Analytical Models
// ============================================================================

export interface AnalyticalMetrics {
  utilization: number;
  erlang_c?: number;
  mean_waiting_time: number;
  mean_queue_length: number;
  mean_response_time: number;
  mean_system_size?: number;
  coefficient_of_variation?: number;
  [key: string]: number | undefined;
}

export interface AnalyticalResponse {
  model_type: QueueModelType;
  config: MMNConfig | MGNConfig | TandemQueueConfig;
  metrics: AnalyticalMetrics;
  formulas_used: string[];
}

// ============================================================================
// Distributed Systems Models
// ============================================================================

export interface RaftRequest {
  num_nodes: number;
  simulation_time: number;
}

export interface VectorClockRequest {
  num_processes: number;
}

export interface TwoPhaseCommitRequest {
  num_participants: number;
  vote_yes_probability: number;
  simulation_time: number;
}

export interface RaftNode {
  node_id: number;
  role: 'follower' | 'candidate' | 'leader';
  term: number;
  voted_for: number | null;
  log_length: number;
}

export interface RaftResults {
  leader_node_id: number | null;
  num_nodes: number;
  simulation_time: number;
  leader_elected: boolean;
  total_elections: number;
  nodes_status: RaftNode[];
}

export interface VectorClockEvent {
  type: 'local' | 'send' | 'receive';
  process: number;
  vector_clock: number[];
}

export interface VectorClockResults {
  num_processes: number;
  events: VectorClockEvent[];
  causality_example: {
    event_a: { process: number; clock: number[] };
    event_b: { process: number; clock: number[] };
    relationship: 'happened_before' | 'happened_after' | 'concurrent';
  };
  total_events: number;
}

export interface TwoPhaseCommitTransaction {
  transaction_id: number;
  decision: 'commit' | 'abort';
  votes: boolean[];
}

export interface TwoPhaseCommitResults {
  num_participants: number;
  vote_yes_probability: number;
  simulation_time: number;
  total_transactions: number;
  committed: number;
  aborted: number;
  commit_rate: number;
  transactions: TwoPhaseCommitTransaction[];
}

export interface DistributedSimulationResponse {
  simulation_id: string;
  protocol: 'Raft' | 'Vector Clocks' | 'Two-Phase Commit';
  results: RaftResults | VectorClockResults | TwoPhaseCommitResults;
  message: string;
  created_at: string;
}

// ============================================================================
// WebSocket Messages
// ============================================================================

export interface WebSocketMessage {
  type: 'connected' | 'status' | 'metrics' | 'completed' | 'error';
  simulation_id?: string;
  status?: string;
  progress?: number;
  message?: string;
  data?: any;
  results?: any;
}

// ============================================================================
// Chart Data
// ============================================================================

export interface TimeSeriesDataPoint {
  time: number;
  value: number;
}

export interface DistributionDataPoint {
  x: number;
  y: number;
}

export interface ComparisonDataPoint {
  metric: string;
  simulation: number;
  analytical: number;
  error: number;
}

// ============================================================================
// UI State
// ============================================================================

export interface ConfigFormState {
  isValid: boolean;
  errors: Record<string, string>;
  warnings: Record<string, string>;
}

export interface SimulationRunState {
  isRunning: boolean;
  progress: number;
  currentMetrics?: Partial<SimulationMetrics>;
  error?: string;
}
