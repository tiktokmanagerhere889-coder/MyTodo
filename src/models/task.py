'''
Task model for the Todo application
Defines the structure and behavior of a task object
'''

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.id}: {self.title}"