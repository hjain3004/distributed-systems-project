"""
Raft Consensus Protocol Implementation

Based on Ongaro & Ousterhout (2014) "In Search of an Understandable Consensus Algorithm"
and distributed systems course material (Midterm content).

Implements:
- Leader election with randomized timeouts
- Log replication for message operations
- Commit protocol requiring majority agreement
- Safety guarantees (election safety, leader append-only, etc.)
"""

import simpy
import random
from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


class RaftState(Enum):
    """Raft node states"""
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


@dataclass
class LogEntry:
    """
    Replicated log entry

    Each entry contains:
    - term: Election term when entry was created
    - operation: Message operation (publish, ack, delete)
    - data: Operation data (message ID, content, etc.)
    """
    term: int
    operation: str
    data: Dict[str, Any]
    index: int = 0


@dataclass
class RaftMessage:
    """Messages exchanged between Raft nodes"""
    msg_type: str  # "vote_request", "vote_response", "append_entries", "append_response"
    term: int
    sender_id: int
    data: Dict[str, Any] = field(default_factory=dict)


class RaftNode:
    """
    Single Raft consensus node

    Implements Raft consensus algorithm with:
    - Leader election
    - Log replication
    - Commit protocol
    """

    def __init__(self,
                 env: simpy.Environment,
                 node_id: int,
                 cluster_size: int,
                 election_timeout_min: float = 10.0,
                 election_timeout_max: float = 20.0,
                 heartbeat_interval: float = 5.0):
        """
        Args:
            env: SimPy environment
            node_id: Unique node ID
            cluster_size: Total number of nodes in cluster
            election_timeout_min: Minimum election timeout (sec)
            election_timeout_max: Maximum election timeout (sec)
            heartbeat_interval: Leader heartbeat interval (sec)
        """
        self.env = env
        self.node_id = node_id
        self.cluster_size = cluster_size
        self.election_timeout_min = election_timeout_min
        self.election_timeout_max = election_timeout_max
        self.heartbeat_interval = heartbeat_interval

        # Raft persistent state (all servers)
        self.current_term = 0
        self.voted_for: Optional[int] = None
        self.log: List[LogEntry] = []

        # Raft volatile state (all servers)
        self.commit_index = 0
        self.last_applied = 0

        # Raft volatile state (leaders only)
        self.next_index: Dict[int, int] = {}  # For each server, index of next log entry to send
        self.match_index: Dict[int, int] = {}  # For each server, highest log entry known to be replicated

        # Node state
        self.state = RaftState.FOLLOWER
        self.leader_id: Optional[int] = None

        # Election state
        self.votes_received: Dict[int, bool] = {}  # Track votes for current term

        # Communication
        self.inbox = simpy.Store(env)
        self.outboxes: Dict[int, simpy.Store] = {}  # Set by cluster

        # Timers
        self.election_timer = None
        self.heartbeat_timer = None

        # Metrics
        self.elections_started = 0
        self.elections_won = 0
        self.heartbeats_sent = 0
        self.log_entries_replicated = 0

    def start(self):
        """Start Raft node processes"""
        self.env.process(self._run())
        self._reset_election_timer()

    def _run(self):
        """Main Raft node event loop"""
        while True:
            # Process incoming messages
            msg = yield self.inbox.get()

            if msg.msg_type == "vote_request":
                self._handle_vote_request(msg)
            elif msg.msg_type == "vote_response":
                self._handle_vote_response(msg)
            elif msg.msg_type == "append_entries":
                self._handle_append_entries(msg)
            elif msg.msg_type == "append_response":
                self._handle_append_response(msg)

    def _reset_election_timer(self, interrupt_current=True):
        """Reset election timeout with randomized duration"""
        if self.election_timer is not None and interrupt_current:
            try:
                self.election_timer.interrupt()
            except RuntimeError:
                # Already interrupted or process can't interrupt itself
                pass

        timeout = random.uniform(self.election_timeout_min, self.election_timeout_max)
        self.election_timer = self.env.process(self._election_timeout(timeout))

    def _election_timeout(self, timeout: float):
        """Election timeout - triggers leader election"""
        try:
            yield self.env.timeout(timeout)

            # Timeout occurred - start election
            if self.state != RaftState.LEADER:
                self._start_election(from_timeout=True)

        except simpy.Interrupt:
            # Timer was reset
            pass

    def _start_election(self, from_timeout=False):
        """Start leader election process"""
        # Become candidate
        self.state = RaftState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.elections_started += 1

        # Reset and track votes (vote for self)
        self.votes_received = {self.node_id: True}

        # Request votes from all other nodes
        for node_id in range(self.cluster_size):
            if node_id != self.node_id and node_id in self.outboxes:
                vote_request = RaftMessage(
                    msg_type="vote_request",
                    term=self.current_term,
                    sender_id=self.node_id,
                    data={
                        'last_log_index': len(self.log),
                        'last_log_term': self.log[-1].term if self.log else 0
                    }
                )
                self.outboxes[node_id].put(vote_request)

        # Reset election timer (don't interrupt if called from timeout)
        self._reset_election_timer(interrupt_current=not from_timeout)

    def _handle_vote_request(self, msg: RaftMessage):
        """Handle RequestVote RPC"""
        # Update term if behind
        if msg.term > self.current_term:
            self._step_down(msg.term)

        grant_vote = False

        if msg.term == self.current_term:
            # Grant vote if haven't voted or already voted for this candidate
            if self.voted_for is None or self.voted_for == msg.sender_id:
                # Check log is up-to-date
                last_log_index = len(self.log)
                last_log_term = self.log[-1].term if self.log else 0

                candidate_log_ok = (
                    msg.data['last_log_term'] > last_log_term or
                    (msg.data['last_log_term'] == last_log_term and
                     msg.data['last_log_index'] >= last_log_index)
                )

                if candidate_log_ok:
                    self.voted_for = msg.sender_id
                    grant_vote = True
                    self._reset_election_timer()

        # Send vote response
        if msg.sender_id in self.outboxes:
            response = RaftMessage(
                msg_type="vote_response",
                term=self.current_term,
                sender_id=self.node_id,
                data={'vote_granted': grant_vote}
            )
            self.outboxes[msg.sender_id].put(response)

    def _handle_vote_response(self, msg: RaftMessage):
        """Handle vote response from another node"""
        if self.state != RaftState.CANDIDATE:
            return

        if msg.term > self.current_term:
            self._step_down(msg.term)
            return

        if msg.term == self.current_term and msg.data.get('vote_granted'):
            # Track vote
            self.votes_received[msg.sender_id] = True

            # Count votes
            votes = sum(1 for granted in self.votes_received.values() if granted)

            # Check if won election (majority)
            if votes > self.cluster_size // 2:
                self._become_leader()

    def _become_leader(self):
        """Transition to leader state"""
        self.state = RaftState.LEADER
        self.leader_id = self.node_id
        self.elections_won += 1

        # Initialize leader state
        for node_id in range(self.cluster_size):
            if node_id != self.node_id:
                self.next_index[node_id] = len(self.log) + 1
                self.match_index[node_id] = 0

        # Cancel election timer
        if self.election_timer is not None:
            self.election_timer.interrupt()

        # Start heartbeat timer
        self.heartbeat_timer = self.env.process(self._send_heartbeats())

    def _send_heartbeats(self):
        """Send periodic heartbeats (empty AppendEntries)"""
        while self.state == RaftState.LEADER:
            # Send AppendEntries to all followers
            for node_id in range(self.cluster_size):
                if node_id != self.node_id and node_id in self.outboxes:
                    prev_log_index = self.next_index.get(node_id, 1) - 1
                    prev_log_term = self.log[prev_log_index - 1].term if prev_log_index > 0 and prev_log_index <= len(self.log) else 0

                    append_msg = RaftMessage(
                        msg_type="append_entries",
                        term=self.current_term,
                        sender_id=self.node_id,
                        data={
                            'prev_log_index': prev_log_index,
                            'prev_log_term': prev_log_term,
                            'entries': [],  # Heartbeat - no entries
                            'leader_commit': self.commit_index
                        }
                    )
                    self.outboxes[node_id].put(append_msg)

            self.heartbeats_sent += 1
            yield self.env.timeout(self.heartbeat_interval)

    def _handle_append_entries(self, msg: RaftMessage):
        """Handle AppendEntries RPC (heartbeat or log replication)"""
        # Update term if behind
        if msg.term > self.current_term:
            self._step_down(msg.term)

        success = False

        if msg.term == self.current_term:
            # Recognize leader
            if self.state != RaftState.FOLLOWER:
                self._step_down(msg.term)

            self.leader_id = msg.sender_id
            self._reset_election_timer()

            # Check log consistency
            prev_log_index = msg.data['prev_log_index']
            prev_log_term = msg.data['prev_log_term']

            log_ok = (
                prev_log_index == 0 or
                (prev_log_index <= len(self.log) and
                 self.log[prev_log_index - 1].term == prev_log_term)
            )

            if log_ok:
                success = True

                # Append new entries
                entries = msg.data.get('entries', [])
                if entries:
                    # Delete conflicting entries and append new ones
                    self.log = self.log[:prev_log_index]
                    self.log.extend(entries)
                    self.log_entries_replicated += len(entries)

                # Update commit index
                leader_commit = msg.data['leader_commit']
                if leader_commit > self.commit_index:
                    self.commit_index = min(leader_commit, len(self.log))

        # Send response
        if msg.sender_id in self.outboxes:
            response = RaftMessage(
                msg_type="append_response",
                term=self.current_term,
                sender_id=self.node_id,
                data={
                    'success': success,
                    'match_index': len(self.log) if success else 0
                }
            )
            self.outboxes[msg.sender_id].put(response)

    def _handle_append_response(self, msg: RaftMessage):
        """Handle AppendEntries response"""
        if self.state != RaftState.LEADER:
            return

        if msg.term > self.current_term:
            self._step_down(msg.term)
            return

        if msg.data.get('success'):
            # Update next_index and match_index
            self.match_index[msg.sender_id] = msg.data['match_index']
            self.next_index[msg.sender_id] = msg.data['match_index'] + 1

            # Update commit_index if majority replicated
            for n in range(self.commit_index + 1, len(self.log) + 1):
                if self.log[n - 1].term == self.current_term:
                    count = 1  # Self
                    for node_id in range(self.cluster_size):
                        if node_id != self.node_id and self.match_index.get(node_id, 0) >= n:
                            count += 1

                    if count > self.cluster_size // 2:
                        self.commit_index = n

        else:
            # Decrement next_index and retry
            self.next_index[msg.sender_id] = max(1, self.next_index[msg.sender_id] - 1)

    def _step_down(self, new_term: int):
        """Step down to follower state"""
        self.current_term = new_term
        self.state = RaftState.FOLLOWER
        self.voted_for = None
        self.leader_id = None

        # Cancel timers
        if self.heartbeat_timer is not None:
            self.heartbeat_timer.interrupt()
            self.heartbeat_timer = None

        self._reset_election_timer()

    def append_log_entry(self, operation: str, data: Dict[str, Any]) -> bool:
        """
        Append new log entry (only leader)

        Args:
            operation: Operation type (e.g., "publish", "ack", "delete")
            data: Operation data

        Returns:
            True if successfully appended (only if leader)
        """
        if self.state != RaftState.LEADER:
            return False

        # Create log entry
        entry = LogEntry(
            term=self.current_term,
            operation=operation,
            data=data,
            index=len(self.log) + 1
        )

        self.log.append(entry)
        return True

    def is_committed(self, log_index: int) -> bool:
        """Check if log entry is committed"""
        return log_index <= self.commit_index

    def get_metrics(self) -> Dict:
        """Get Raft node metrics"""
        return {
            'node_id': self.node_id,
            'state': self.state.value,
            'term': self.current_term,
            'leader_id': self.leader_id,
            'log_size': len(self.log),
            'commit_index': self.commit_index,
            'elections_started': self.elections_started,
            'elections_won': self.elections_won,
            'heartbeats_sent': self.heartbeats_sent,
            'log_entries_replicated': self.log_entries_replicated,
        }


class RaftCluster:
    """
    Raft consensus cluster manager

    Creates and manages a cluster of Raft nodes with simulated network
    """

    def __init__(self,
                 env: simpy.Environment,
                 num_nodes: int = 3,
                 election_timeout_min: float = 10.0,
                 election_timeout_max: float = 20.0,
                 heartbeat_interval: float = 5.0):
        """
        Args:
            env: SimPy environment
            num_nodes: Number of nodes in cluster (odd number recommended)
            election_timeout_min: Minimum election timeout
            election_timeout_max: Maximum election timeout
            heartbeat_interval: Leader heartbeat interval
        """
        self.env = env
        self.num_nodes = num_nodes

        # Create Raft nodes
        self.nodes: List[RaftNode] = []
        for i in range(num_nodes):
            node = RaftNode(
                env=env,
                node_id=i,
                cluster_size=num_nodes,
                election_timeout_min=election_timeout_min,
                election_timeout_max=election_timeout_max,
                heartbeat_interval=heartbeat_interval
            )
            self.nodes.append(node)

        # Connect nodes (simulated network)
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j:
                    self.nodes[i].outboxes[j] = self.nodes[j].inbox

        # Start all nodes
        for node in self.nodes:
            node.start()

    def get_leader(self) -> Optional[RaftNode]:
        """Get current leader node"""
        for node in self.nodes:
            if node.state == RaftState.LEADER:
                return node
        return None

    def get_cluster_metrics(self) -> List[Dict]:
        """Get metrics for all nodes"""
        return [node.get_metrics() for node in self.nodes]
