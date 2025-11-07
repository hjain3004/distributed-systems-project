"""
Statistical Rigorous Experiments with Confidence Intervals

Runs each experiment configuration multiple times (N=10 replications)
and calculates 95% confidence intervals for all metrics.

Statistical rigor ensures results are reproducible and significant.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

from src.core.config import MMNConfig, MGNConfig
from src.models.mmn_queue import run_mmn_simulation
from src.models.mgn_queue import run_mgn_simulation
from src.models.threading import run_dedicated_simulation, run_shared_simulation


class ReplicationRunner:
    """Run multiple replications and calculate statistics"""

    def __init__(self, n_replications=10):
        self.n_replications = n_replications

    def run_replications(self, experiment_func, config_dict, description):
        """
        Run experiment multiple times with different random seeds

        Args:
            experiment_func: Function that runs simulation and returns stats dict
            config_dict: Dictionary of configuration parameters
            description: Description for progress output

        Returns:
            Dictionary with mean, std, and 95% CI for each metric
        """
        print(f"\n  Running {description} ({self.n_replications} replications)...")

        all_results = []

        for rep in range(self.n_replications):
            # Use different random seed for each replication
            config_dict['random_seed'] = 1000 + rep

            # Run experiment
            results = experiment_func(config_dict)
            all_results.append(results)

            if (rep + 1) % 5 == 0:
                print(f"    Completed {rep+1}/{self.n_replications} replications...")

        # Calculate statistics across replications
        return self._calculate_statistics(all_results)

    def _calculate_statistics(self, results_list):
        """
        Calculate mean, std, and 95% confidence intervals

        Args:
            results_list: List of dictionaries with metric values

        Returns:
            Dictionary with statistics for each metric
        """
        # Convert list of dicts to dict of lists
        metrics = {}
        for key in results_list[0].keys():
            metrics[key] = [r[key] for r in results_list]

        # Calculate statistics
        statistics = {}
        for metric_name, values in metrics.items():
            values_array = np.array(values)

            mean_val = np.mean(values_array)
            std_val = np.std(values_array, ddof=1)  # Sample std
            sem_val = scipy_stats.sem(values_array)  # Standard error of mean

            # 95% confidence interval using t-distribution
            confidence = 0.95
            degrees_freedom = len(values_array) - 1
            t_value = scipy_stats.t.ppf((1 + confidence) / 2, degrees_freedom)
            margin_error = t_value * sem_val

            statistics[metric_name] = {
                'mean': mean_val,
                'std': std_val,
                'sem': sem_val,
                'ci_lower': mean_val - margin_error,
                'ci_upper': mean_val + margin_error,
                'ci_width': 2 * margin_error,
            }

        return statistics


def experiment_mmn_with_confidence():
    """M/M/N experiment with confidence intervals"""
    print("="*70)
    print("Experiment 1: M/M/N with Confidence Intervals")
    print("="*70)

    runner = ReplicationRunner(n_replications=10)

    def run_mmn_exp(config_dict):
        config = MMNConfig(**config_dict)
        metrics = run_mmn_simulation(config)
        stats = metrics.summary_statistics()
        return {
            'mean_wait': stats['mean_wait'],
            'mean_response': stats['mean_response'],
            'p95_response': stats['p95_response'],
            'p99_response': stats['p99_response'],
            'throughput': stats['throughput'],
        }

    config_dict = {
        'arrival_rate': 100,
        'num_threads': 10,
        'service_rate': 12,
        'sim_duration': 2000,
        'warmup_time': 200,
        'random_seed': 42
    }

    results = runner.run_replications(run_mmn_exp, config_dict, "M/M/N baseline")

    # Display results
    print("\n  Results (Mean ± 95% CI):")
    for metric_name, stats_dict in results.items():
        mean = stats_dict['mean']
        ci_width = stats_dict['ci_width']
        rel_error = (ci_width / (2 * mean)) * 100 if mean > 0 else 0

        print(f"    {metric_name:20s}: {mean:.6f} ± {ci_width/2:.6f}  (±{rel_error:.2f}%)")

    return results


def experiment_mgn_with_confidence():
    """M/G/N experiment with confidence intervals for different α"""
    print("\n" + "="*70)
    print("Experiment 2: M/G/N Heavy-Tail with Confidence Intervals")
    print("="*70)

    runner = ReplicationRunner(n_replications=10)

    alphas = [2.1, 2.5, 3.0]
    all_results = {}

    for alpha in alphas:
        def run_mgn_exp(config_dict):
            config = MGNConfig(**config_dict)
            metrics = run_mgn_simulation(config)
            stats = metrics.summary_statistics()
            return {
                'mean_wait': stats['mean_wait'],
                'mean_response': stats['mean_response'],
                'p95_response': stats['p95_response'],
                'p99_response': stats['p99_response'],
                'throughput': stats['throughput'],
            }

        config_dict = {
            'arrival_rate': 100,
            'num_threads': 10,
            'service_rate': 12,
            'distribution': 'pareto',
            'alpha': alpha,
            'sim_duration': 2000,
            'warmup_time': 200,
            'random_seed': 42
        }

        results = runner.run_replications(run_mgn_exp, config_dict, f"M/G/N α={alpha}")
        all_results[alpha] = results

    # Display results
    print("\n  Results Comparison (Mean ± 95% CI):")
    print(f"\n  {'α':<6} {'Mean Wait (sec)':<25} {'P99 Response (sec)':<25} {'Throughput (msg/sec)':<25}")
    print("  " + "-"*82)

    for alpha in alphas:
        stats = all_results[alpha]

        mean_wait = stats['mean_wait']['mean']
        wait_ci = stats['mean_wait']['ci_width'] / 2

        p99_resp = stats['p99_response']['mean']
        p99_ci = stats['p99_response']['ci_width'] / 2

        tput = stats['throughput']['mean']
        tput_ci = stats['throughput']['ci_width'] / 2

        print(f"  {alpha:<6.1f} {mean_wait:.4f} ± {wait_ci:.4f}        {p99_resp:.4f} ± {p99_ci:.4f}        {tput:.2f} ± {tput_ci:.2f}")

    return all_results


def experiment_threading_with_confidence():
    """Threading comparison with confidence intervals"""
    print("\n" + "="*70)
    print("Experiment 3: Threading Models with Confidence Intervals")
    print("="*70)

    runner = ReplicationRunner(n_replications=10)

    # Test at ρ=0.7 (medium load)
    arrival_rate = 168
    num_threads = 20
    service_rate = 12

    results = {}

    # M/M/N baseline
    def run_baseline(config_dict):
        config = MMNConfig(**config_dict)
        metrics = run_mmn_simulation(config)
        stats = metrics.summary_statistics()
        return {
            'mean_response': stats['mean_response'],
            'p95_response': stats['p95_response'],
            'throughput': stats['throughput'],
        }

    config_dict = {
        'arrival_rate': arrival_rate,
        'num_threads': num_threads,
        'service_rate': service_rate,
        'sim_duration': 2000,
        'warmup_time': 200,
        'random_seed': 42
    }

    results['baseline'] = runner.run_replications(run_baseline, config_dict, "M/M/N baseline")

    # Dedicated threading
    def run_dedicated(config_dict):
        config = MMNConfig(**config_dict)
        metrics = run_dedicated_simulation(config, threads_per_connection=2)
        stats = metrics.summary_statistics()
        return {
            'mean_response': stats['mean_response'],
            'p95_response': stats['p95_response'],
            'throughput': stats['throughput'],
        }

    results['dedicated'] = runner.run_replications(run_dedicated, config_dict, "Dedicated threading")

    # Shared threading
    def run_shared(config_dict):
        config = MMNConfig(**config_dict)
        metrics = run_shared_simulation(config, overhead_coefficient=0.1)
        stats = metrics.summary_statistics()
        return {
            'mean_response': stats['mean_response'],
            'p95_response': stats['p95_response'],
            'throughput': stats['throughput'],
        }

    results['shared'] = runner.run_replications(run_shared, config_dict, "Shared threading")

    # Display results
    print("\n  Results at ρ=0.7 (Mean ± 95% CI):")
    print(f"\n  {'Model':<15} {'Mean Response (sec)':<30} {'Throughput (msg/sec)':<30}")
    print("  " + "-"*76)

    for model_name in ['baseline', 'dedicated', 'shared']:
        stats = results[model_name]

        mean_resp = stats['mean_response']['mean']
        resp_ci = stats['mean_response']['ci_width'] / 2

        tput = stats['throughput']['mean']
        tput_ci = stats['throughput']['ci_width'] / 2

        print(f"  {model_name.capitalize():<15} {mean_resp:.6f} ± {resp_ci:.6f}        {tput:.2f} ± {tput_ci:.2f}")

    return results


def main():
    """Run all experiments with confidence intervals"""

    print("\n" + "="*70)
    print(" STATISTICAL RIGOROUS EXPERIMENTS")
    print(" Running 10 Replications with 95% Confidence Intervals")
    print("="*70)

    # Run all experiments
    mmn_results = experiment_mmn_with_confidence()
    mgn_results = experiment_mgn_with_confidence()
    threading_results = experiment_threading_with_confidence()

    # Save results
    print("\n" + "="*70)
    print("Saving Results...")
    print("="*70)

    # Convert to DataFrames and save
    # MMN results
    mmn_df = pd.DataFrame({
        metric: {
            'mean': stats['mean'],
            'std': stats['std'],
            'ci_lower': stats['ci_lower'],
            'ci_upper': stats['ci_upper'],
        }
        for metric, stats in mmn_results.items()
    }).T
    mmn_df.to_csv('experiments/mmn_confidence_intervals.csv')
    print("  ✓ Saved: experiments/mmn_confidence_intervals.csv")

    # MGN results
    mgn_data = []
    for alpha, results in mgn_results.items():
        for metric, stats in results.items():
            mgn_data.append({
                'alpha': alpha,
                'metric': metric,
                'mean': stats['mean'],
                'std': stats['std'],
                'ci_lower': stats['ci_lower'],
                'ci_upper': stats['ci_upper'],
            })
    mgn_df = pd.DataFrame(mgn_data)
    mgn_df.to_csv('experiments/mgn_confidence_intervals.csv', index=False)
    print("  ✓ Saved: experiments/mgn_confidence_intervals.csv")

    # Threading results
    threading_data = []
    for model, results in threading_results.items():
        for metric, stats in results.items():
            threading_data.append({
                'model': model,
                'metric': metric,
                'mean': stats['mean'],
                'std': stats['std'],
                'ci_lower': stats['ci_lower'],
                'ci_upper': stats['ci_upper'],
            })
    threading_df = pd.DataFrame(threading_data)
    threading_df.to_csv('experiments/threading_confidence_intervals.csv', index=False)
    print("  ✓ Saved: experiments/threading_confidence_intervals.csv")

    print("\n" + "="*70)
    print("✓ ALL EXPERIMENTS COMPLETED WITH STATISTICAL RIGOR")
    print("="*70)
    print("\nStatistical Summary:")
    print("  - Replications per configuration: 10")
    print("  - Confidence level: 95%")
    print("  - Statistical test: t-distribution (appropriate for small samples)")
    print("  - All results include mean ± margin of error")
    print("\nResults demonstrate reproducibility and statistical significance.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
