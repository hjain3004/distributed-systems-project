"""
Message Ordering Modes

Implements Section 3 of Li et al. (2015) - Message Consistency Options:
1. In-order delivery (FIFO)
2. Out-of-order delivery (random sampling for performance)
"""

from collections import OrderedDict
from typing import Optional, List
import random
from .cloud_message import CloudMessage, MessageState


class MessageOrdering:
    """
    Message ordering and consistency manager

    Based on Li et al. (2015) Section 3: Message Consistency
    """

    def __init__(self, mode: str = "out_of_order"):
        """
        Args:
            mode: Either "in_order" (FIFO) or "out_of_order" (random sampling)
        """
        if mode not in ["in_order", "out_of_order"]:
            raise ValueError(f"Invalid mode: {mode}. Must be 'in_order' or 'out_of_order'")

        self.mode = mode
        self.messages: OrderedDict[int, CloudMessage] = OrderedDict()
        self.sequence_number = 0

    def enqueue(self, message: CloudMessage):
        """
        Add message with ordering guarantee

        Args:
            message: Message to enqueue
        """
        if self.mode == "in_order":
            # Maintain strict FIFO order
            message.vector_clock = [self.sequence_number]
            self.messages[message.id] = message
            self.sequence_number += 1
        else:
            # Out-of-order: no sequence guarantee
            self.messages[message.id] = message

    def dequeue(self) -> Optional[CloudMessage]:
        """
        Retrieve message based on consistency mode

        Returns:
            CloudMessage if available, None otherwise
        """
        if not self.messages:
            return None

        if self.mode == "in_order":
            # FIFO: Get oldest message by insertion order
            message_id = next(iter(self.messages))
            return self.messages.pop(message_id)
        else:
            # Out-of-order: Random sampling (models distributed storage)
            # Paper: "one of the nodes is randomly sampled"
            message_id = random.choice(list(self.messages.keys()))
            return self.messages.pop(message_id)

    def peek(self) -> Optional[CloudMessage]:
        """
        View next message without removing

        Returns:
            CloudMessage if available, None otherwise
        """
        if not self.messages:
            return None

        if self.mode == "in_order":
            message_id = next(iter(self.messages))
        else:
            message_id = random.choice(list(self.messages.keys()))

        return self.messages[message_id]

    def get_visible_messages(self, current_time: float) -> List[CloudMessage]:
        """
        Get all currently visible messages

        Args:
            current_time: Current simulation time

        Returns:
            List of visible messages
        """
        visible = []
        for message in self.messages.values():
            if message.is_visible(current_time):
                visible.append(message)
        return visible

    def size(self) -> int:
        """Get number of messages in queue"""
        return len(self.messages)

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.messages) == 0


class FIFOQueue(MessageOrdering):
    """FIFO (First-In-First-Out) message queue"""

    def __init__(self):
        super().__init__(mode="in_order")


class RandomSamplingQueue(MessageOrdering):
    """Random sampling queue (out-of-order for performance)"""

    def __init__(self):
        super().__init__(mode="out_of_order")
