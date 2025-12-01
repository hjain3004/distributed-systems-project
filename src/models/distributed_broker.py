"""
Distributed Message Broker

Implements distributed storage with replication as described in
Li et al. (2015) for cloud message broker architecture.

Features:
- Multi-node distributed storage
- Configurable replication factor
- Consistent hashing for load distribution
- Fault tolerance
"""

import simpy
import random
from typing import List, Optional, Dict
from .cloud_message import CloudMessage, MessageState
from .visibility_timeout import VisibilityTimeoutManager
from .message_ordering import MessageOrdering


class StorageNode:
    """
    Single storage node in distributed broker

    Each node has its own visibility timeout manager
    """

    def __init__(self, env: simpy.Environment, node_id: int,
                 ordering_mode: str = "out_of_order"):
        """
        Args:
            env: SimPy environment
            node_id: Unique node identifier
            ordering_mode: "in_order" or "out_of_order"
        """
        self.env = env
        self.node_id = node_id
        self.visibility_manager = VisibilityTimeoutManager(env)
        self.ordering = MessageOrdering(mode=ordering_mode)

        # Node-level metrics
        self.messages_stored = 0
        self.messages_received = 0

    def store_message(self, message: CloudMessage):
        """Store message in this node"""
        self.ordering.enqueue(message)
        self.visibility_manager.add_message(message)
        self.messages_stored += 1

    def receive_message(self) -> Optional[CloudMessage]:
        """Receive message from this node"""
        if self.ordering.mode == "in_order":
            # In-Order Delivery: HOL Blocking Logic
            # 1. Peek at the next EXPECTED message from ordering buffer
            next_msg = self.ordering.peek()
            
            if next_msg is None:
                # Buffer empty or next sequence not yet arrived
                return None
                
            # 2. Check if this specific message is available and visible
            if self.visibility_manager.is_visible(next_msg.id):
                # 3. Receive it
                message = self.visibility_manager.receive_specific_message(next_msg.id)
                if message:
                    # 4. Advance sequence in ordering buffer
                    self.ordering.dequeue()
                    self.messages_received += 1
                return message
            else:
                # HOL Blocking: Next expected message is not visible
                # (It might be processing, or not yet in visibility manager)
                # print(f"HOL Blocking: Waiting for {next_msg.id} (Queue Index: {self.ordering.queue_index})")
                return None
        else:
            # Out-of-Order: Just get any visible message
            message = self.visibility_manager.receive_message()
            if message:
                self.messages_received += 1
            return message

    def acknowledge_message(self, message_id: int) -> bool:
        """Acknowledge message on this node"""
        return self.visibility_manager.acknowledge_message(message_id)

    def get_queue_depth(self) -> int:
        """Get number of visible messages"""
        return self.visibility_manager.get_queue_depth()


class ConsistentHashRing:
    """
    Consistent hashing for message distribution

    Based on distributed systems course material (Quiz 1)
    """

    def __init__(self, num_nodes: int, num_virtual_nodes: int = 150):
        """
        Args:
            num_nodes: Number of physical nodes
            num_virtual_nodes: Virtual nodes per physical node
        """
        self.num_nodes = num_nodes
        self.num_virtual_nodes = num_virtual_nodes

        # Build hash ring
        self.ring = {}
        self.sorted_keys = []
        self._build_ring()

    def _build_ring(self):
        """Build consistent hash ring with virtual nodes"""
        for node_id in range(self.num_nodes):
            for vnode in range(self.num_virtual_nodes):
                # Hash: node_id + virtual node number
                hash_key = hash(f"node_{node_id}_vnode_{vnode}")
                self.ring[hash_key] = node_id

        self.sorted_keys = sorted(self.ring.keys())

    def get_node(self, message_id: int) -> int:
        """
        Get primary node for message

        Args:
            message_id: Message identifier

        Returns:
            Node ID
        """
        if not self.sorted_keys:
            return 0

        # Hash message ID
        msg_hash = hash(message_id)

        # Find first node clockwise on ring
        for key in self.sorted_keys:
            if msg_hash <= key:
                return self.ring[key]

        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]

    def get_replicas(self, primary_node: int, replication_factor: int) -> List[int]:
        """
        Get replica nodes for a message

        Args:
            primary_node: Primary node ID
            replication_factor: Number of replicas

        Returns:
            List of node IDs (including primary)
        """
        replicas = [primary_node]

        # Get next N-1 distinct nodes
        next_node = (primary_node + 1) % self.num_nodes
        while len(replicas) < min(replication_factor, self.num_nodes):
            if next_node not in replicas:
                replicas.append(next_node)
            next_node = (next_node + 1) % self.num_nodes

        return replicas


class DistributedBroker:
    """
    Distributed message broker with replication

    Models cloud message broker architecture from Li et al. (2015)
    with multiple storage nodes and configurable replication.
    """

    def __init__(self, env: simpy.Environment,
                 num_nodes: int = 3,
                 replication_factor: int = 3,
                 ordering_mode: str = "out_of_order"):
        """
        Args:
            env: SimPy environment
            num_nodes: Number of storage nodes
            replication_factor: Number of replicas per message
            ordering_mode: "in_order" or "out_of_order"
        """
        self.env = env
        self.num_nodes = num_nodes
        self.replication_factor = min(replication_factor, num_nodes)
        self.ordering_mode = ordering_mode

        # Create storage nodes
        self.nodes: List[StorageNode] = []
        for i in range(num_nodes):
            node = StorageNode(env, node_id=i, ordering_mode=ordering_mode)
            self.nodes.append(node)

        # Consistent hashing for distribution
        self.hash_ring = ConsistentHashRing(num_nodes)

        # Broker-level metrics
        self.total_messages_published = 0
        self.total_messages_received = 0
        self.total_acks = 0

    def publish_message(self, message: CloudMessage):
        """
        Publish message to broker (replicate to N nodes)

        Args:
            message: Message to publish
        """
        # Get primary node using consistent hashing
        primary_node = self.hash_ring.get_node(message.id)

        # Get replica nodes
        replica_nodes = self.hash_ring.get_replicas(
            primary_node, self.replication_factor
        )

        # Store message on all replica nodes
        message.replication_nodes = replica_nodes
        for node_id in replica_nodes:
            # Create a copy for each replica
            message_copy = CloudMessage(
                id=message.id,
                content=message.content,
                arrival_time=message.arrival_time,
                visibility_timeout=message.visibility_timeout,
                max_receive_count=message.max_receive_count
            )
            message_copy.replication_nodes = replica_nodes
            self.nodes[node_id].store_message(message_copy)

        self.total_messages_published += 1

    def receive_message(self) -> Optional[CloudMessage]:
        """
        Receive message from broker

        Paper: "one of the nodes is randomly sampled"
        Implements random node sampling for load balancing

        Returns:
            CloudMessage if available, None otherwise
        """
        # Random node sampling (models SQS/Azure Queue behavior)
        sampled_node = random.choice(self.nodes)

        message = sampled_node.receive_message()
        if message:
            self.total_messages_received += 1

        return message

    def acknowledge_message(self, message: CloudMessage) -> bool:
        """
        Acknowledge message (delete from ALL replicas)

        Args:
            message: Message to acknowledge

        Returns:
            True if acknowledged successfully
        """
        # Acknowledge on all replica nodes
        success_count = 0
        for node_id in message.replication_nodes:
            if self.nodes[node_id].acknowledge_message(message.id):
                success_count += 1

        if success_count > 0:
            self.total_acks += 1

        # Success if acknowledged on majority of replicas
        return success_count > len(message.replication_nodes) // 2

    def get_total_queue_depth(self) -> int:
        """Get total messages across all nodes (with replication)"""
        return sum(node.get_queue_depth() for node in self.nodes)

    def get_unique_message_count(self) -> int:
        """
        Get count of unique messages (accounting for replication)

        Approximate: total / replication_factor
        """
        total = self.get_total_queue_depth()
        return total // self.replication_factor if self.replication_factor > 0 else total

    def get_node_metrics(self) -> List[Dict]:
        """Get metrics for each node"""
        metrics = []
        for node in self.nodes:
            node_metrics = {
                'node_id': node.node_id,
                'queue_depth': node.get_queue_depth(),
                'messages_stored': node.messages_stored,
                'messages_received': node.messages_received,
                **node.visibility_manager.get_metrics()
            }
            metrics.append(node_metrics)
        return metrics

    def get_broker_metrics(self) -> Dict:
        """Get broker-level metrics"""
        return {
            'num_nodes': self.num_nodes,
            'replication_factor': self.replication_factor,
            'total_messages_published': self.total_messages_published,
            'total_messages_received': self.total_messages_received,
            'total_acks': self.total_acks,
            'total_queue_depth': self.get_total_queue_depth(),
            'unique_message_count': self.get_unique_message_count(),
        }
