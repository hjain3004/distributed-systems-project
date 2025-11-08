"""
CAP Theorem Analysis for Cloud Message Brokers

Implements CAP theorem trade-off analysis for distributed message brokers.
Based on distributed systems course material (Quiz 1, Midterm).

CAP Theorem states you can only achieve 2 out of 3:
- Consistency (C): All nodes see the same data
- Availability (A): System always responds
- Partition Tolerance (P): System works despite network partitions

In practice, network partitions are inevitable, so we choose between:
- CP: Consistent & Partition-tolerant (e.g., HBase, MongoDB)
- AP: Available & Partition-tolerant (e.g., AWS SQS, Cassandra)
"""

from enum import Enum
from typing import Dict, Optional
import numpy as np


class CAPMode(Enum):
    """CAP theorem configuration modes"""
    CP = "CP"  # Consistency + Partition tolerance (sacrifice availability)
    AP = "AP"  # Availability + Partition tolerance (sacrifice consistency)
    CA = "CA"  # Consistency + Availability (not realistic in distributed systems)


class CAPAnalysis:
    """
    Analyze CAP trade-offs for cloud message brokers

    Based on Quiz 1 and Midterm course material
    """

    def __init__(self, mode: CAPMode = CAPMode.AP):
        """
        Args:
            mode: CAP configuration mode
        """
        self.mode = mode

        # Metrics tracking
        self.partition_events = 0
        self.blocked_operations = 0
        self.inconsistent_reads = 0
        self.total_operations = 0

    def handle_partition(self, partition_detected: bool) -> dict:
        """
        Handle network partition based on CAP choice

        Args:
            partition_detected: Whether partition is detected

        Returns:
            Decision dictionary with actions to take
        """
        if partition_detected:
            self.partition_events += 1

            if self.mode == CAPMode.CP:
                # CP: Maintain consistency, sacrifice availability
                # Block operations to minority partition
                self.blocked_operations += 1
                return {
                    'allow_writes': False,
                    'allow_reads': False,
                    'reason': 'Maintaining consistency during partition',
                    'action': 'block_until_partition_healed'
                }

            elif self.mode == CAPMode.AP:
                # AP: Maintain availability, allow inconsistency
                # Continue operating with eventual consistency
                return {
                    'allow_writes': True,
                    'allow_reads': True,
                    'reason': 'Maintaining availability with eventual consistency',
                    'action': 'continue_with_eventual_consistency'
                }

            elif self.mode == CAPMode.CA:
                # CA: Not realistic in real distributed systems
                # Network partitions are inevitable
                return {
                    'allow_writes': False,
                    'allow_reads': False,
                    'reason': 'CA mode invalid in partitioned network',
                    'action': 'error'
                }
        else:
            # No partition - all modes work normally
            return {
                'allow_writes': True,
                'allow_reads': True,
                'reason': 'No partition detected',
                'action': 'normal_operation'
            }

    def get_consistency_guarantee(self) -> str:
        """Get consistency guarantee for current mode"""
        guarantees = {
            CAPMode.CP: "Strong consistency (linearizability)",
            CAPMode.AP: "Eventual consistency",
            CAPMode.CA: "Strong consistency (no partition tolerance)"
        }
        return guarantees[self.mode]

    def get_availability_guarantee(self) -> str:
        """Get availability guarantee for current mode"""
        guarantees = {
            CAPMode.CP: "Reduced availability during partitions",
            CAPMode.AP: "High availability (always responds)",
            CAPMode.CA: "High availability (no partitions)"
        }
        return guarantees[self.mode]

    def analyze_tradeoffs(self) -> Dict:
        """
        Comprehensive CAP trade-off analysis

        Returns:
            Dictionary with trade-off analysis
        """
        if self.mode == CAPMode.CP:
            return {
                'mode': 'CP',
                'consistency': 'Strong (linearizable)',
                'availability': 'Reduced during partitions (majority required)',
                'partition_tolerance': 'Yes',
                'latency': 'Higher (need majority consensus)',
                'use_cases': [
                    'Financial transactions',
                    'Banking systems',
                    'Inventory management',
                    'Strongly consistent data stores (HBase, MongoDB)'
                ],
                'message_broker_behavior': {
                    'during_partition': 'Block minority partition operations',
                    'consistency_model': 'Strong consistency',
                    'message_ordering': 'Strict FIFO',
                    'duplicate_prevention': 'Guaranteed',
                },
                'pros': [
                    'No data inconsistency',
                    'Guaranteed ordering',
                    'No duplicates'
                ],
                'cons': [
                    'System may be unavailable during partitions',
                    'Higher latency',
                    'Reduced throughput'
                ]
            }

        elif self.mode == CAPMode.AP:
            return {
                'mode': 'AP',
                'consistency': 'Eventual (may see stale data)',
                'availability': 'Always available',
                'partition_tolerance': 'Yes',
                'latency': 'Lower (local operations)',
                'use_cases': [
                    'Social media feeds',
                    'Caching systems',
                    'DNS',
                    'AWS SQS / Azure Queue Storage (as in paper)'
                ],
                'message_broker_behavior': {
                    'during_partition': 'Continue operations, accept inconsistency',
                    'consistency_model': 'Eventual consistency',
                    'message_ordering': 'Best-effort / out-of-order',
                    'duplicate_prevention': 'At-least-once delivery (may duplicate)',
                },
                'pros': [
                    'Always available',
                    'Low latency',
                    'High throughput'
                ],
                'cons': [
                    'May see stale/inconsistent data',
                    'Possible message duplicates',
                    'Ordering not guaranteed'
                ]
            }

        else:  # CA mode
            return {
                'mode': 'CA',
                'consistency': 'Strong',
                'availability': 'High',
                'partition_tolerance': 'No',
                'latency': 'Low',
                'use_cases': [
                    'Single-datacenter RDBMS',
                    'Not realistic for distributed systems'
                ],
                'message_broker_behavior': {
                    'during_partition': 'System fails',
                    'consistency_model': 'Strong consistency',
                    'message_ordering': 'Strict FIFO',
                    'duplicate_prevention': 'Guaranteed',
                },
                'pros': [
                    'Strong consistency',
                    'High availability (when no partitions)'
                ],
                'cons': [
                    'No partition tolerance',
                    'Not viable for cloud deployments',
                    'Single point of failure'
                ]
            }

    def calculate_availability(self, partition_probability: float,
                               partition_duration: float,
                               total_time: float) -> float:
        """
        Calculate effective availability under CAP choice

        Args:
            partition_probability: Probability of partition occurring
            partition_duration: Average partition duration
            total_time: Total observation time

        Returns:
            Availability percentage (0-100)
        """
        if self.mode == CAPMode.CP:
            # CP: Unavailable during partitions
            expected_partition_time = partition_probability * partition_duration
            unavailable_time = expected_partition_time
            availability = ((total_time - unavailable_time) / total_time) * 100

        elif self.mode == CAPMode.AP:
            # AP: Always available
            availability = 100.0

        elif self.mode == CAPMode.CA:
            # CA: Unavailable if any partition occurs
            availability = (1 - partition_probability) * 100

        return availability

    def get_metrics(self) -> Dict:
        """Get CAP analysis metrics"""
        return {
            'mode': self.mode.value,
            'partition_events': self.partition_events,
            'blocked_operations': self.blocked_operations,
            'inconsistent_reads': self.inconsistent_reads,
            'total_operations': self.total_operations,
            'block_rate': self.blocked_operations / self.total_operations if self.total_operations > 0 else 0,
        }


def compare_cap_modes():
    """
    Compare different CAP configurations

    Returns comprehensive comparison for report/presentation
    """
    print("="*70)
    print("CAP THEOREM ANALYSIS - Cloud Message Brokers")
    print("="*70)

    modes = [CAPMode.CP, CAPMode.AP]

    for mode in modes:
        analyzer = CAPAnalysis(mode=mode)
        analysis = analyzer.analyze_tradeoffs()

        print(f"\n{'-'*70}")
        print(f"MODE: {analysis['mode']}")
        print(f"{'-'*70}")
        print(f"Consistency:          {analysis['consistency']}")
        print(f"Availability:         {analysis['availability']}")
        print(f"Partition Tolerance:  {analysis['partition_tolerance']}")
        print(f"Latency:              {analysis['latency']}")

        print(f"\nUse Cases:")
        for use_case in analysis['use_cases']:
            print(f"  - {use_case}")

        print(f"\nMessage Broker Behavior:")
        for key, value in analysis['message_broker_behavior'].items():
            print(f"  {key}: {value}")

        # Calculate availability for sample scenario
        availability = analyzer.calculate_availability(
            partition_probability=0.01,  # 1% chance of partition
            partition_duration=60,        # 60 sec average duration
            total_time=3600               # 1 hour observation
        )
        print(f"\nEffective Availability: {availability:.2f}%")
        print(f"  (with 1% partition probability, 60 sec duration)")

    print("\n" + "="*70)
    print("RECOMMENDATION FOR CLOUD MESSAGE BROKER")
    print("="*70)
    print("AWS SQS / Azure Queue (as in Li et al. paper): AP mode")
    print("  - Favors availability over strict consistency")
    print("  - Uses eventual consistency model")
    print("  - Implements visibility timeout for reliability")
    print("  - At-least-once delivery (may have duplicates)")
    print("="*70 + "\n")


if __name__ == "__main__":
    compare_cap_modes()
