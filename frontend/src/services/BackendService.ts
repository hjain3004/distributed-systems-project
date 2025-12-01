import { SimulationConfig } from '../context/SimulationContext';

const API_BASE = 'http://localhost:3100/api';

export const BackendService = {
    async runSimulation(config: SimulationConfig) {
        let endpoint = '/simulations/mmn';
        let body: any = {
            arrival_rate: config.lambda,
            num_threads: config.numServers,
            service_rate: config.mu,
            enable_qos: config.enableQoS, // Add QoS flag
            sim_duration: 1000,
            warmup_time: 100
        };

        if (config.serverType === 'heterogeneous' || config.legacyPercentage > 0 || config.workStealing) {
            endpoint = '/simulations/heterogeneous';
            // Convert percentage to server groups
            // Total 5 servers. 
            // If 20% legacy -> 1 legacy, 4 normal.
            // If 40% legacy -> 2 legacy, 3 normal.
            const numLegacy = Math.round((config.legacyPercentage / 100) * config.numServers);
            const numNormal = config.numServers - numLegacy;

            body = {
                arrival_rate: config.lambda,
                server_groups: [
                    { count: numLegacy, service_rate: config.mu / 4, name: 'legacy' },
                    { count: numNormal, service_rate: config.mu, name: 'normal' }
                ],
                selection_policy: config.workStealing ? 'work_stealing' : 'random', // Naive
                consistency_mode: config.consistencyMode, // Pass consistency mode
                sim_duration: 1000,
                warmup_time: 100
            };
        } else if (config.distribution === 'pareto' || config.distribution.startsWith('erlang') || config.loadShedding) {
            // MGN supports Pareto and Erlang
            endpoint = '/simulations/mgn';
            body = {
                arrival_rate: config.lambda,
                num_threads: config.numServers,
                service_rate: config.mu,
                distribution: config.distribution.startsWith('erlang') ? 'erlang' : config.distribution, // Map erlang_k2 -> erlang
                alpha: 1.1, // Only for Pareto
                k: config.distribution === 'erlang_k2' ? 2 : (config.distribution === 'erlang_k5' ? 5 : 1), // For Erlang
                enable_qos: config.enableQoS, // Add QoS flag
                sim_duration: 1000,
                warmup_time: 100,
            };
        } else if (config.consistencyMode !== 'none' || config.ordering !== 'unordered' || config.requestHedging) {
            endpoint = '/simulations/distributed';
            body = {
                arrival_rate: config.lambda,
                service_rate: config.mu * config.numServers, // Aggregate capacity
                num_nodes: 3,
                consistency_mode: config.consistencyMode,
                ordering_mode: config.ordering,
                enable_hedging: config.requestHedging, // Pass the flag
                sim_duration: 1000,
                warmup_time: 100
            };
        }

        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error(`Simulation failed: ${response.statusText}`);
        }

        return response.json();
    },

    async getSimulationResults(simId: string) {
        const response = await fetch(`${API_BASE}/simulations/${simId}/results`);
        if (!response.ok) {
            throw new Error('Failed to fetch results');
        }
        return response.json();
    },

    async getAnalyticalComparison(config: SimulationConfig) {
        // ... implementation for analytical comparison
    }
};
