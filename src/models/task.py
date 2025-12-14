'''
Task model for the Todo application
Defines the structure and behavior of a task object
'''

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """
    Represents a single task in the todo list
    """
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = None
    priority: Priority = Priority.MEDIUM
    tags: list = None
    due_date: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # daily, weekly, monthly, yearly

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.tags is None:
            self.tags = []

    def __str__(self):
        status = "✓" if self.completed else "○"
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[self.priority.value]
        return f"[{status}] {priority_emoji} {self.id}: {self.title}"