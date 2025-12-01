"""Performance metrics calculation and storage"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import numpy as np
import pandas as pd


@dataclass
class SimulationMetrics:
    """Container for simulation results"""

    # Raw data
    wait_times: List[float] = field(default_factory=list)
    service_times: List[float] = field(default_factory=list)
    queue_lengths: List[int] = field(default_factory=list)
    system_sizes: List[int] = field(default_factory=list)
    arrival_times: List[float] = field(default_factory=list)
    departure_times: List[float] = field(default_factory=list)

    # Configuration
    model_name: str = ""
    config: Dict[str, Any] = field(default_factory=dict)

    def response_times(self) -> List[float]:
        """Calculate response times (wait + service)"""
        return [w + s for w, s in zip(self.wait_times, self.service_times)]

    def summary_statistics(self) -> Dict[str, float]:
        """Calculate comprehensive summary statistics"""

        if not self.wait_times:
            return {}

        wait_times = np.array(self.wait_times)
        response_times = np.array(self.response_times())
        queue_lengths = np.array(self.queue_lengths) if self.queue_lengths else np.array([0])

        return {
            # Waiting time statistics
            'mean_wait': float(np.mean(wait_times)),
            'median_wait': float(np.median(wait_times)),
            'std_wait': float(np.std(wait_times)),
            'p95_wait': float(np.percentile(wait_times, 95)),
            'p99_wait': float(np.percentile(wait_times, 99)),
            'max_wait': float(np.max(wait_times)),

            # Response time statistics
            'mean_response': float(np.mean(response_times)),
            'p50_response': float(np.percentile(response_times, 50)),
            'p95_response': float(np.percentile(response_times, 95)),
            'p99_response': float(np.percentile(response_times, 99)),

            # Queue statistics
            'mean_queue_length': float(np.mean(queue_lengths)),
            'max_queue_length': float(np.max(queue_lengths)),
            'p95_queue_length': float(np.percentile(queue_lengths, 95)),

            # Throughput
            'throughput': float(len(self.wait_times) / (max(self.departure_times) - min(self.arrival_times))) if self.departure_times and self.arrival_times else 0.0,

            # Service time statistics
            'mean_service': float(np.mean(self.service_times)) if self.service_times else 0.0,
            'cv_service': float(np.std(self.service_times) / np.mean(self.service_times)) if self.service_times and np.mean(self.service_times) > 0 else 0.0,
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame for analysis"""

        if not self.wait_times:
            return pd.DataFrame()

        return pd.DataFrame({
            'arrival_time': self.arrival_times,
            'wait_time': self.wait_times,
            'service_time': self.service_times,
            'response_time': self.response_times(),
            'queue_length': self.queue_lengths if len(self.queue_lengths) == len(self.wait_times) else [0] * len(self.wait_times),
            'departure_time': self.departure_times,
        })

    def save(self, filepath: str):
        """Save metrics to CSV"""
        df = self.to_dataframe()
        df.to_csv(filepath, index=False)

    @classmethod
    def load(cls, filepath: str) -> 'SimulationMetrics':
        """Load metrics from CSV"""
        df = pd.read_csv(filepath)

        metrics = cls(
            arrival_times=df['arrival_time'].tolist(),
            wait_times=df['wait_time'].tolist(),
            service_times=df['service_time'].tolist(),
            queue_lengths=df['queue_length'].tolist(),
            departure_times=df['departure_time'].tolist(),
        )
        return metrics


@dataclass
class ComparisonResults:
    """Compare multiple models"""

    models: Dict[str, SimulationMetrics]

    def comparison_table(self) -> pd.DataFrame:
        """Generate comparison table"""

        rows = []
        for name, metrics in self.models.items():
            stats = metrics.summary_statistics()
            if stats:
                stats['model'] = name
                rows.append(stats)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df = df.set_index('model')
        return df

    def relative_performance(self, baseline: str) -> pd.DataFrame:
        """Calculate relative performance vs baseline"""

        table = self.comparison_table()
        if table.empty or baseline not in table.index:
            return pd.DataFrame()

        baseline_stats = table.loc[baseline]

        relative = table.div(baseline_stats, axis=1)
        return relative
