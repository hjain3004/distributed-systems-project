import React, { createContext, useContext, useState, ReactNode } from 'react';

export type DistributionType = 'exponential' | 'pareto' | 'erlang_k2' | 'erlang_k5';
export type ConsistencyType = 'none' | 'eventual' | 'strong_2pc' | 'raft';
export type ServerType = 'homogeneous' | 'heterogeneous';
export type OrderingType = 'unordered' | 'strict_fifo';

export interface SimulationConfig {
    distribution: DistributionType;
    consistencyMode: ConsistencyType;
    serverType: ServerType;
    ordering: OrderingType;
    lambda: number; // Arrival Rate
    mu: number;     // Service Rate
    numServers: number;
    legacyPercentage: number; // 0 to 50%
    // Advanced Cures
    // Advanced Cures
    workStealing: boolean;
    loadShedding: boolean;
    requestHedging: boolean;
    enableQoS: boolean;
}

interface SimulationContextType {
    config: SimulationConfig;
    setConfig: (config: SimulationConfig) => void;
    updateConfig: (updates: Partial<SimulationConfig>) => void;
    isRunning: boolean;
    setIsRunning: (isRunning: boolean) => void;
    // Helper to reset to defaults
    resetConfig: () => void;
}

const defaultConfig: SimulationConfig = {
    distribution: 'exponential',
    consistencyMode: 'none',
    serverType: 'homogeneous',
    ordering: 'unordered',
    lambda: 50,
    mu: 12,
    numServers: 5,
    legacyPercentage: 0,
    workStealing: false,
    loadShedding: false,
    requestHedging: false,
    enableQoS: false
};

const SimulationContext = createContext<SimulationContextType | undefined>(undefined);

export const SimulationProvider = ({ children }: { children: ReactNode }) => {
    const [config, setConfig] = useState<SimulationConfig>(defaultConfig);
    const [isRunning, setIsRunning] = useState(false);

    const updateConfig = (updates: Partial<SimulationConfig>) => {
        setConfig(prev => ({ ...prev, ...updates }));
    };

    const resetConfig = () => {
        setConfig(defaultConfig);
        setIsRunning(false);
    };

    return (
        <SimulationContext.Provider value={{
            config,
            setConfig,
            updateConfig,
            isRunning,
            setIsRunning,
            resetConfig
        }}>
            {children}
        </SimulationContext.Provider>
    );
};

export const useSimulation = () => {
    const context = useContext(SimulationContext);
    if (context === undefined) {
        throw new Error('useSimulation must be used within a SimulationProvider');
    }
    return context;
};
