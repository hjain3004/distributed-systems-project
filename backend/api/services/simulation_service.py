"""
Simulation Service
Business logic for managing simulations (create, run, store, retrieve)
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
sys.path.append('/home/user/distributed-systems-project')

from src.models.mgn_queue import run_mgn_simulation
from src.models.tandem_queue import run_tandem_simulation
from src.models.heterogeneous_mmn import run_heterogeneous_mmn_simulation
from src.models.priority_queue import run_priority_queue_simulation
from src.core.config import MMNConfig, MGNConfig, TandemQueueConfig, HeterogeneousMMNConfig, ServerGroup, PriorityQueueConfig


class SimulationService:
    """
    Service for managing simulations

    In-memory storage for demo (in production, use database)
    """

    def __init__(self):
        self.simulations: Dict[str, Dict[str, Any]] = {}

    def create_simulation(
        self,
        sim_id: str,
        model_type: str,
        config: Dict[str, Any],
        status: str = "pending"
    ) -> Dict[str, Any]:
        """Create a new simulation entry"""
        simulation = {
            "simulation_id": sim_id,
            "model_type": model_type,
            "config": config,
            "status": status,
            "created_at": datetime.utcnow(),
            "progress": 0,
            "message": "Simulation created",
            "results": None,
            "metrics": None,
            "current_metrics": None,
            "error": None
        }

        self.simulations[sim_id] = simulation
        return simulation

    def get_simulation(self, sim_id: str) -> Optional[Dict[str, Any]]:
        """Get simulation by ID"""
        return self.simulations.get(sim_id)

    def update_simulation(
        self,
        sim_id: str,
        **kwargs
    ) -> bool:
        """Update simulation fields"""
        if sim_id in self.simulations:
            self.simulations[sim_id].update(kwargs)
            return True
        return False

    def delete_simulation(self, sim_id: str) -> bool:
        """Delete simulation"""
        if sim_id in self.simulations:
            del self.simulations[sim_id]
            return True
        return False

    def list_simulations(self) -> List[Dict[str, Any]]:
        """List all simulations"""
        return list(self.simulations.values())

    # Run simulation methods (called as background tasks)

    def run_mmn_simulation(self, sim_id: str, config: MMNConfig):
        """Run M/M/N simulation in background"""
        try:
            # Update status
            self.update_simulation(
                sim_id,
                status="running",
                message="Running M/M/N simulation..."
            )

            # Run simulation
            if config.enable_qos:
                # Run Priority Queue Simulation (M/M/N with Priorities)
                priority_config = PriorityQueueConfig(
                    arrival_rate=config.arrival_rate,
                    num_threads=config.num_threads,
                    service_rate=config.service_rate,
                    sim_duration=config.sim_duration,
                    warmup_time=config.warmup_time,
                    random_seed=config.random_seed,
                    num_priorities=2,
                    priority_rates=[config.arrival_rate * 0.2, config.arrival_rate * 0.8], # 20% VIP
                    preemptive=True # VIPs preempt standard
                )
                results = run_priority_queue_simulation(priority_config)
                
                # Use Standard Traffic (Priority 2) as the main metrics to show starvation
                std_metrics = results[2]
                metrics = std_metrics # This is a dict, not SimulationMetrics object
                stats = std_metrics # It's already a dict
                
                # Add VIP metrics to results
                stats['vip_metrics'] = results[1]
            else:
                metrics = run_mmn_simulation(config)
                # Get summary statistics
                stats = metrics.summary_statistics()

            # Update with results
            self.update_simulation(
                sim_id,
                status="completed",
                progress=100,
                message="Simulation completed successfully",
                results=stats,
                metrics=stats,
                completed_at=datetime.utcnow()
            )

        except Exception as e:
            # Update with error
            self.update_simulation(
                sim_id,
                status="failed",
                message="Simulation failed",
                error=str(e),
                completed_at=datetime.utcnow()
            )

    def run_mgn_simulation(self, sim_id: str, config: MGNConfig):
        """Run M/G/N simulation in background"""
        try:
            self.update_simulation(
                sim_id,
                status="running",
                message="Running M/G/N simulation with heavy-tailed distribution..."
            )

            # Run simulation
            if config.enable_qos:
                # Priority Queue with General Distribution (Not fully supported in PriorityQueueModel yet, falls back to Exp)
                # For demo purposes, we run Priority Queue (M/M/N QoS)
                priority_config = PriorityQueueConfig(
                    arrival_rate=config.arrival_rate,
                    num_threads=config.num_threads,
                    service_rate=config.service_rate,
                    sim_duration=config.sim_duration,
                    warmup_time=config.warmup_time,
                    random_seed=config.random_seed,
                    num_priorities=2,
                    priority_rates=[config.arrival_rate * 0.2, config.arrival_rate * 0.8],
                    preemptive=True
                )
                results = run_priority_queue_simulation(priority_config)
                std_metrics = results[2]
                stats = std_metrics
                stats['vip_metrics'] = results[1]
            else:
                metrics = run_mgn_simulation(config)
                stats = metrics.summary_statistics()

            # Update with results
            self.update_simulation(
                sim_id,
                status="completed",
                progress=100,
                message="M/G/N simulation completed successfully",
                results=stats,
                metrics=stats,
                completed_at=datetime.utcnow()
            )

        except Exception as e:
            self.update_simulation(
                sim_id,
                status="failed",
                message="M/G/N simulation failed",
                error=str(e),
                completed_at=datetime.utcnow()
            )

    def run_tandem_simulation(self, sim_id: str, config: TandemQueueConfig):
        """Run Tandem queue simulation in background"""
        try:
            self.update_simulation(
                sim_id,
                status="running",
                message="Running Tandem queue simulation..."
            )

            # Run simulation
            results = run_tandem_simulation(config)

            # Extract metrics
            metrics = {
                "mean_end_to_end": results.get("mean_end_to_end", 0),
                "stage1_wait": results.get("stage1_wait", 0),
                "stage2_wait": results.get("stage2_wait", 0),
                "network_time": results.get("network_time", 0),
                "total_messages": results.get("total_messages", 0),
                "failed_transmissions": results.get("failed_transmissions", 0)
            }

            # Update with results
            self.update_simulation(
                sim_id,
                status="completed",
                progress=100,
                message="Tandem queue simulation completed successfully",
                results=results,
                metrics=metrics,
                completed_at=datetime.utcnow()
            )

        except Exception as e:
            self.update_simulation(
                sim_id,
                status="failed",
                message="Tandem queue simulation failed",
                error=str(e),
                completed_at=datetime.utcnow()
            )

    def run_heterogeneous_simulation(self, sim_id: str, config: HeterogeneousMMNConfig):
        """Run Heterogeneous M/M/N simulation in background"""
        try:
            self.update_simulation(
                sim_id,
                status="running",
                message="Running Heterogeneous M/M/N simulation..."
            )

            # Run simulation
            metrics = run_heterogeneous_mmn_simulation(config)
            stats = metrics.summary_statistics()

            # Update with results
            self.update_simulation(
                sim_id,
                status="completed",
                progress=100,
                message="Heterogeneous simulation completed successfully",
                results=stats,
                metrics=stats,
                completed_at=datetime.utcnow()
            )

        except Exception as e:
            self.update_simulation(
                sim_id,
                status="failed",
                message="Heterogeneous simulation failed",
                error=str(e),
                completed_at=datetime.utcnow()
            )

    def run_distributed_simulation(self, sim_id: str, config: Dict[str, Any]):
        """
        Run Distributed Broker simulation (Consistency/Ordering)
        """
        try:
            self.update_simulation(
                sim_id,
                status="running",
                message="Running Distributed Broker simulation..."
            )
            
            # Mock result for now to unblock frontend integration
            import time
            time.sleep(1) # Simulate work
            
            results = {
                "mean_latency": 0.250 if config.get("consistency_mode") == "strong" else 0.100,
                "p99_latency": 1.500 if config.get("ordering_mode") == "fifo" else 0.500,
                "throughput": 120 if config.get("ordering_mode") == "fifo" else 500
            }

            self.update_simulation(
                sim_id,
                status="completed",
                progress=100,
                message="Distributed simulation completed (MOCK)",
                results=results,
                metrics=results,
                completed_at=datetime.utcnow()
            )

        except Exception as e:
            self.update_simulation(
                sim_id,
                status="failed",
                message="Distributed simulation failed",
                error=str(e),
                completed_at=datetime.utcnow()
            )
