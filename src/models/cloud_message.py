"""
Cloud Message Model - Core Data Structures

Implements the cloud message broker model from Li et al. (2015)
with visibility timeout, message states, and reliability guarantees.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time


class MessageState(Enum):
    """Message visibility states (Paper Section 6.4)"""
    VISIBLE = "visible"
    INVISIBLE = "invisible"
    DELETED = "deleted"
    IN_DLQ = "in_dlq"  # Dead Letter Queue


@dataclass
class CloudMessage:
    """
    Cloud message with visibility timeout and reliability features

    Based on AWS SQS and Azure Queue Storage patterns described
    in Li et al. (2015) Section 6.
    """
    id: int
    content: str
    arrival_time: float

    # Visibility timeout (Paper Section 6.4, Figure 9)
    visibility_timeout: float = 30.0  # AWS SQS default: 30 seconds
    state: MessageState = MessageState.VISIBLE

    # Reliability tracking
    receive_count: int = 0
    max_receive_count: int = 3  # After 3 failures, move to DLQ

    # Distributed storage metadata
    replication_nodes: list = field(default_factory=list)
    vector_clock: list = field(default_factory=list)

    # Timing metadata
    first_receive_time: Optional[float] = None
    last_receive_time: Optional[float] = None
    invisible_until: Optional[float] = None

    # Processing metadata
    processing_started: Optional[float] = None
    processing_completed: Optional[float] = None

    def make_invisible(self, current_time: float):
        """
        Make message invisible after receive (Paper Figure 9)

        Args:
            current_time: Current simulation time
        """
        self.state = MessageState.INVISIBLE
        self.receive_count += 1
        self.last_receive_time = current_time
        self.invisible_until = current_time + self.visibility_timeout

        if self.first_receive_time is None:
            self.first_receive_time = current_time

    def make_visible(self):
        """Make message visible again after timeout"""
        if self.state == MessageState.INVISIBLE:
            self.state = MessageState.VISIBLE
            self.invisible_until = None

    def delete(self):
        """Delete message after successful acknowledgment"""
        self.state = MessageState.DELETED

    def move_to_dlq(self):
        """Move to Dead Letter Queue after max retries"""
        self.state = MessageState.IN_DLQ

    def is_visible(self, current_time: float) -> bool:
        """Check if message is currently visible"""
        if self.state == MessageState.VISIBLE:
            return True
        elif self.state == MessageState.INVISIBLE:
            # Check if visibility timeout has expired
            if self.invisible_until and current_time >= self.invisible_until:
                self.make_visible()
                return True
        return False

    def is_poison_message(self) -> bool:
        """Check if message has exceeded retry limit"""
        return self.receive_count >= self.max_receive_count

    def get_age(self, current_time: float) -> float:
        """Get message age in seconds"""
        return current_time - self.arrival_time

    def __hash__(self):
        """Hash based on message content for duplicate detection"""
        return hash((self.id, self.content))
