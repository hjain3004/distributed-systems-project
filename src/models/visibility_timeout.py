"""
Visibility Timeout Manager

Implements the visibility timeout mechanism from Li et al. (2015) Section 6.4
and Figure 9 (Visibility Timeout Subnet).

This is the core reliability guarantee for cloud message brokers like AWS SQS.
"""

import simpy
from typing import Dict, Optional, List
from .cloud_message import CloudMessage, MessageState


class VisibilityTimeoutManager:
    """
    Manages message visibility states and timeout mechanisms

    Based on Li et al. (2015) Figure 9: Visibility Timeout Subnet
    """

    def __init__(self, env: simpy.Environment, enable_dlq: bool = True):
        """
        Args:
            env: SimPy environment
            enable_dlq: Enable Dead Letter Queue for poison messages
        """
        self.env = env
        self.enable_dlq = enable_dlq

        # Message storage
        self.visible_messages: Dict[int, CloudMessage] = {}
        self.invisible_messages: Dict[int, CloudMessage] = {}
        self.deleted_messages: Dict[int, CloudMessage] = {}
        self.dlq_messages: Dict[int, CloudMessage] = {}

        # Active timers
        self.timers: Dict[int, simpy.events.Process] = {}

        # Metrics
        self.total_receives = 0
        self.total_acks = 0
        self.total_timeouts = 0
        self.total_dlq = 0

    def add_message(self, message: CloudMessage):
        """
        Add new message to queue (visible state)

        Args:
            message: Cloud message to add
        """
        message.state = MessageState.VISIBLE
        self.visible_messages[message.id] = message

    def receive_message(self) -> Optional[CloudMessage]:
        """
        Receive (dequeue) a visible message

        Implements:
        1. Get visible message
        2. Make invisible
        3. Start visibility timer

        Returns:
            CloudMessage if available, None otherwise
        """
        if not self.visible_messages:
            return None

        # Get first visible message (FIFO for now)
        message_id = next(iter(self.visible_messages))
        message = self.visible_messages.pop(message_id)

        # Make invisible and start timer (Paper Figure 9)
        message.make_invisible(self.env.now)
        self.invisible_messages[message.id] = message

        # Start visibility timeout timer
        self.timers[message.id] = self.env.process(
            self._visibility_timer(message)
        )

        self.total_receives += 1

        return message

    def _visibility_timer(self, message: CloudMessage):
        """
        Visibility timeout timer process (Paper Figure 9)

        After visibility_timeout seconds:
        - If message still invisible → make visible (retry)
        - If message exceeds max retries → move to DLQ

        Args:
            message: Message being timed
        """
        try:
            # Wait for visibility timeout
            yield self.env.timeout(message.visibility_timeout)

            # Check if message is still invisible
            if message.id in self.invisible_messages:
                # Timeout occurred - message not acknowledged

                # Check for poison message
                if message.is_poison_message() and self.enable_dlq:
                    # Too many retries - move to DLQ
                    self._move_to_dlq(message)
                else:
                    # Make visible again for retry
                    self._make_visible_again(message)

                self.total_timeouts += 1

        except simpy.Interrupt:
            # Timer was interrupted (message was acknowledged)
            pass

    def acknowledge_message(self, message_id: int) -> bool:
        """
        Acknowledge successful message processing (delete message)

        Args:
            message_id: ID of message to acknowledge

        Returns:
            True if acknowledged, False if message not found
        """
        if message_id in self.invisible_messages:
            message = self.invisible_messages.pop(message_id)
            message.delete()
            message.processing_completed = self.env.now
            self.deleted_messages[message_id] = message

            # Cancel visibility timer
            if message_id in self.timers:
                self.timers[message_id].interrupt()
                del self.timers[message_id]

            self.total_acks += 1
            return True

        return False

    def _make_visible_again(self, message: CloudMessage):
        """Make message visible again after timeout (retry)"""
        if message.id in self.invisible_messages:
            self.invisible_messages.pop(message.id)
            message.make_visible()
            self.visible_messages[message.id] = message

    def _move_to_dlq(self, message: CloudMessage):
        """Move poison message to Dead Letter Queue"""
        if message.id in self.invisible_messages:
            self.invisible_messages.pop(message.id)
            message.move_to_dlq()
            self.dlq_messages[message.id] = message
            self.total_dlq += 1

    def get_queue_depth(self) -> int:
        """Get number of visible messages"""
        return len(self.visible_messages)

    def get_invisible_count(self) -> int:
        """Get number of invisible (in-flight) messages"""
        return len(self.invisible_messages)

    def get_dlq_depth(self) -> int:
        """Get number of messages in Dead Letter Queue"""
        return len(self.dlq_messages)

    def get_metrics(self) -> dict:
        """Get visibility timeout metrics"""
        return {
            'visible_messages': len(self.visible_messages),
            'invisible_messages': len(self.invisible_messages),
            'deleted_messages': len(self.deleted_messages),
            'dlq_messages': len(self.dlq_messages),
            'total_receives': self.total_receives,
            'total_acks': self.total_acks,
            'total_timeouts': self.total_timeouts,
            'total_dlq': self.total_dlq,
            'ack_rate': self.total_acks / self.total_receives if self.total_receives > 0 else 0,
            'timeout_rate': self.total_timeouts / self.total_receives if self.total_receives > 0 else 0,
            'dlq_rate': self.total_dlq / self.total_receives if self.total_receives > 0 else 0,
        }
