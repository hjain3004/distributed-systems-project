"""
Vector Clocks for Causality Tracking

Based on Lamport (1978) "Time, Clocks, and the Ordering of Events in a Distributed System"
and distributed systems course material (Quiz 1, Midterm).

Implements:
- Vector clock timestamps for distributed events
- Happened-before (→) relationship detection
- Concurrent event detection
- Causality preservation for message ordering
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class VectorClock:
    """
    Vector clock for distributed event ordering

    Each process maintains a vector of logical clocks:
    - VC[i] = number of events that occurred at process i
    - VC is updated on local events, send, and receive
    """

    num_processes: int
    process_id: int
    clock: List[int] = field(default_factory=list)

    def __post_init__(self):
        """Initialize vector clock to all zeros"""
        if not self.clock:
            self.clock = [0] * self.num_processes

    def tick(self):
        """
        Increment local clock on local event

        Rule: On local event at process i
        VC[i] = VC[i] + 1
        """
        self.clock[self.process_id] += 1

    def send_event(self) -> List[int]:
        """
        Prepare timestamp for sending message

        Rule: On send event at process i
        1. VC[i] = VC[i] + 1
        2. Send VC with message

        Returns:
            Copy of vector clock to send with message
        """
        self.clock[self.process_id] += 1
        return deepcopy(self.clock)

    def receive_event(self, received_clock: List[int]):
        """
        Update clock on receiving message

        Rule: On receive event at process i
        1. VC[i] = VC[i] + 1
        2. VC[j] = max(VC[j], received_VC[j]) for all j != i

        Args:
            received_clock: Vector clock from received message
        """
        # Merge clocks (take max of each component)
        for j in range(self.num_processes):
            if j != self.process_id:
                self.clock[j] = max(self.clock[j], received_clock[j])

        # Increment local clock
        self.clock[self.process_id] += 1

    def happened_before(self, other_clock: List[int]) -> bool:
        """
        Check if this event happened before another event

        Event e1 → e2 (happened-before) if:
        VC(e1) < VC(e2)

        Which means:
        - VC(e1)[i] <= VC(e2)[i] for all i
        - VC(e1)[j] < VC(e2)[j] for at least one j

        Args:
            other_clock: Vector clock to compare against

        Returns:
            True if this happened before other
        """
        less_or_equal = all(
            self.clock[i] <= other_clock[i]
            for i in range(self.num_processes)
        )

        strictly_less = any(
            self.clock[i] < other_clock[i]
            for i in range(self.num_processes)
        )

        return less_or_equal and strictly_less

    def concurrent_with(self, other_clock: List[int]) -> bool:
        """
        Check if this event is concurrent with another event

        Events e1 || e2 (concurrent) if:
        - NOT (e1 → e2)
        - NOT (e2 → e1)

        Args:
            other_clock: Vector clock to compare against

        Returns:
            True if events are concurrent
        """
        e1_before_e2 = self.happened_before(other_clock)

        # Check if other happened before this
        e2_before_e1 = all(
            other_clock[i] <= self.clock[i]
            for i in range(self.num_processes)
        ) and any(
            other_clock[i] < self.clock[i]
            for i in range(self.num_processes)
        )

        # Concurrent if neither happened before the other
        return not (e1_before_e2 or e2_before_e1)

    def equals(self, other_clock: List[int]) -> bool:
        """
        Check if two clocks are equal

        Args:
            other_clock: Vector clock to compare against

        Returns:
            True if clocks are identical
        """
        return self.clock == other_clock

    def get_timestamp(self) -> List[int]:
        """Get current vector clock timestamp"""
        return deepcopy(self.clock)

    def __repr__(self) -> str:
        return f"VC{self.clock}"


class CausalityTracker:
    """
    Tracks causality relationships between distributed events

    Uses vector clocks to:
    1. Determine event ordering (happened-before)
    2. Detect concurrent events
    3. Ensure causal message delivery
    """

    def __init__(self, num_processes: int):
        """
        Args:
            num_processes: Number of processes in distributed system
        """
        self.num_processes = num_processes

        # Vector clocks for each process
        self.clocks: Dict[int, VectorClock] = {}
        for i in range(num_processes):
            self.clocks[i] = VectorClock(num_processes=num_processes, process_id=i)

        # Event history for analysis
        self.events: List[Tuple[int, str, List[int]]] = []

    def local_event(self, process_id: int) -> List[int]:
        """
        Record local event at process

        Args:
            process_id: Process where event occurred

        Returns:
            Updated vector clock
        """
        self.clocks[process_id].tick()
        timestamp = self.clocks[process_id].get_timestamp()
        self.events.append((process_id, "local", timestamp))
        return timestamp

    def send_event(self, process_id: int) -> List[int]:
        """
        Record send event at process

        Args:
            process_id: Process sending message

        Returns:
            Vector clock to attach to message
        """
        timestamp = self.clocks[process_id].send_event()
        self.events.append((process_id, "send", timestamp))
        return timestamp

    def receive_event(self, process_id: int, received_clock: List[int]) -> List[int]:
        """
        Record receive event at process

        Args:
            process_id: Process receiving message
            received_clock: Vector clock from message

        Returns:
            Updated vector clock
        """
        self.clocks[process_id].receive_event(received_clock)
        timestamp = self.clocks[process_id].get_timestamp()
        self.events.append((process_id, "receive", timestamp))
        return timestamp

    def check_causality(self, event1_idx: int, event2_idx: int) -> str:
        """
        Check causality relationship between two events

        Args:
            event1_idx: Index of first event in events list
            event2_idx: Index of second event in events list

        Returns:
            Relationship: "happened_before", "happened_after", "concurrent", or "equal"
        """
        if event1_idx >= len(self.events) or event2_idx >= len(self.events):
            return "invalid"

        _, _, clock1 = self.events[event1_idx]
        _, _, clock2 = self.events[event2_idx]

        # Create temporary vector clocks for comparison
        vc1 = VectorClock(num_processes=self.num_processes, process_id=0, clock=clock1)
        vc2 = VectorClock(num_processes=self.num_processes, process_id=0, clock=clock2)

        if vc1.equals(clock2):
            return "equal"
        elif vc1.happened_before(clock2):
            return "happened_before"
        elif vc2.happened_before(clock1):
            return "happened_after"
        elif vc1.concurrent_with(clock2):
            return "concurrent"
        else:
            return "unknown"

    def can_deliver(self, process_id: int, message_clock: List[int]) -> bool:
        """
        Check if message can be delivered causally

        Causal delivery requires:
        - Message from process j can be delivered at process i if:
          1. message_clock[j] = receiver_clock[j] + 1
          2. message_clock[k] <= receiver_clock[k] for all k != j

        This ensures all causally preceding messages have been delivered.

        Args:
            process_id: Process that would receive message
            message_clock: Vector clock from message

        Returns:
            True if message can be delivered causally
        """
        receiver_clock = self.clocks[process_id].clock

        # Find sender (process with highest clock value in message)
        sender_id = message_clock.index(max(message_clock))

        # Check condition 1: Message is next expected from sender
        if message_clock[sender_id] != receiver_clock[sender_id] + 1:
            return False

        # Check condition 2: All other processes are up-to-date
        for k in range(self.num_processes):
            if k != sender_id:
                if message_clock[k] > receiver_clock[k]:
                    return False

        return True

    def get_current_clocks(self) -> Dict[int, List[int]]:
        """Get current vector clocks for all processes"""
        return {
            process_id: vc.get_timestamp()
            for process_id, vc in self.clocks.items()
        }

    def get_event_history(self) -> List[Tuple[int, str, List[int]]]:
        """Get complete event history"""
        return self.events.copy()


class CausalMessageQueue:
    """
    Message queue with causal ordering guarantees

    Ensures messages are delivered in causal order using vector clocks.
    Holds back messages that arrive out of causal order.
    """

    def __init__(self, process_id: int, num_processes: int):
        """
        Args:
            process_id: ID of this process
            num_processes: Total number of processes
        """
        self.process_id = process_id
        self.num_processes = num_processes

        # Vector clock for this process
        self.vector_clock = VectorClock(
            num_processes=num_processes,
            process_id=process_id
        )

        # Pending messages (waiting for causal dependencies)
        self.pending_messages: List[Tuple[List[int], any]] = []

        # Delivered messages
        self.delivered_count = 0
        self.held_back_count = 0

    def send_message(self, content: any) -> Tuple[List[int], any]:
        """
        Prepare message for sending with vector clock

        Args:
            content: Message content

        Returns:
            Tuple of (vector_clock, content)
        """
        timestamp = self.vector_clock.send_event()
        return (timestamp, content)

    def receive_message(self, timestamp: List[int], content: any) -> Optional[any]:
        """
        Receive message with causal ordering check

        Args:
            timestamp: Vector clock from message
            content: Message content

        Returns:
            Message content if deliverable, None if held back
        """
        # Check if can deliver immediately
        if self._can_deliver(timestamp):
            self.vector_clock.receive_event(timestamp)
            self.delivered_count += 1

            # Check if any pending messages can now be delivered
            self._deliver_pending()

            return content
        else:
            # Hold back message
            self.pending_messages.append((timestamp, content))
            self.held_back_count += 1
            return None

    def _can_deliver(self, message_clock: List[int]) -> bool:
        """Check if message can be delivered causally"""
        receiver_clock = self.vector_clock.clock

        # Find sender
        sender_id = message_clock.index(max(message_clock))

        # Causal delivery conditions
        next_expected = (message_clock[sender_id] == receiver_clock[sender_id] + 1)
        all_caught_up = all(
            message_clock[k] <= receiver_clock[k]
            for k in range(self.num_processes)
            if k != sender_id
        )

        return next_expected and all_caught_up

    def _deliver_pending(self):
        """Try to deliver pending messages"""
        delivered_indices = []

        for i, (timestamp, content) in enumerate(self.pending_messages):
            if self._can_deliver(timestamp):
                self.vector_clock.receive_event(timestamp)
                self.delivered_count += 1
                delivered_indices.append(i)

        # Remove delivered messages from pending queue
        for i in reversed(delivered_indices):
            self.pending_messages.pop(i)

    def get_metrics(self) -> Dict:
        """Get message queue metrics"""
        return {
            'process_id': self.process_id,
            'vector_clock': self.vector_clock.get_timestamp(),
            'delivered_count': self.delivered_count,
            'held_back_count': self.held_back_count,
            'pending_count': len(self.pending_messages),
        }
