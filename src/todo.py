'''
Todo manager for the Todo application
Handles the in-memory storage and operations for tasks
'''

from typing import List, Optional
from .models.task import Task
import uuid


class TodoManager:
    """
    Manages the collection of tasks in memory
    """
    def __init__(self):
        self.tasks: List[Task] = []
        self.next_id = 1
        self.load_tasks()  # Load existing tasks from file

    def add_task(self, title: str, description: Optional[str] = None) -> Task:
        """
        Creates and adds a new task to the in-memory list

        Args:
            title (str): The title of the task (required)
            description (str, optional): The description of the task

        Returns:
            Task: The newly created task object
        """
        # Generate unique ID for the task
        task_id = self.next_id
        self.next_id += 1

        # Create the new task
        new_task = Task(
            id=task_id,
            title=title,
            description=description
        )

        # Add task to the in-memory list
        self.tasks.append(new_task)

        # Save tasks to file
        self.save_tasks()

        return new_task

    def get_all_tasks(self) -> List[Task]:
        """
        Returns all tasks in the in-memory list

        Returns:
            List[Task]: All tasks in the collection
        """
        return self.tasks

    def add_imported_task(self, task: Task) -> bool:
        """
        Adds a task that was imported from a file

        Args:
            task (Task): The task to add

        Returns:
            bool: True if task was added successfully, False otherwise
        """
        # Check if task ID already exists
        for existing_task in self.tasks:
            if existing_task.id == task.id:
                # If ID exists, try to find next available ID
                task.id = self.next_id
                self.next_id += 1
                break

        self.tasks.append(task)
        # Update next_id if necessary
        if task.id >= self.next_id:
            self.next_id = task.id + 1
        self.save_tasks()
        return True

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Finds and returns a task by its ID

        Args:
            task_id (int): The ID of the task to find

        Returns:
            Task or None: The task if found, None otherwise
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> bool:
        """
        Updates an existing task's title and/or description

        Args:
            task_id (int): The ID of the task to update
            title (str, optional): New title for the task
            description (str, optional): New description for the task

        Returns:
            bool: True if task was updated, False if task not found
        """
        task = self.get_task_by_id(task_id)
        if task:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            self.save_tasks()  # Save after update
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """
        Deletes a task by its ID

        Args:
            task_id (int): The ID of the task to delete

        Returns:
            bool: True if task was deleted, False if task not found
        """
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()  # Save after deletion
            return True
        return False

    def toggle_task_status(self, task_id: int) -> bool:
        """
        Toggles the completion status of a task

        Args:
            task_id (int): The ID of the task to toggle

        Returns:
            bool: True if task status was toggled, False if task not found
        """
        task = self.get_task_by_id(task_id)
        if task:
            task.completed = not task.completed
            self.save_tasks()  # Save after status change
            return True
        return False

    def save_tasks(self):
        """Save tasks to JSON file"""
        import json
        from datetime import datetime

        # Prepare tasks for saving
        task_list = []
        for task in self.tasks:
            task_dict = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'completed': task.completed,
                'created_at': task.created_at.strftime("%Y-%m-%d") if task.created_at else datetime.now().strftime("%Y-%m-%d")
            }
            task_list.append(task_dict)

        data = {
            'tasks': task_list,
            'next_id': self.next_id
        }

        with open('tasks.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_tasks(self):
        """Load tasks from JSON file"""
        import json
        import os
        from datetime import datetime

        if os.path.exists('tasks.json'):
            try:
                with open('tasks.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.tasks = []
                for task_data in data.get('tasks', []):
                    # Create task with proper attributes
                    created_at_str = task_data.get('created_at', datetime.now().strftime("%Y-%m-%d"))
                    try:
                        created_at = datetime.strptime(created_at_str, "%Y-%m-%d")
                    except ValueError:
                        created_at = datetime.now()

                    task = Task(
                        id=task_data['id'],
                        title=task_data.get('title', ''),
                        description=task_data.get('description', ''),
                        completed=task_data.get('completed', False),
                        created_at=created_at
                    )
                    self.tasks.append(task)

                self.next_id = data.get('next_id', max([task.id for task in self.tasks], default=0) + 1)
            except (json.JSONDecodeError, KeyError, TypeError):
                # If file is corrupted, start fresh
                self.tasks = []
                self.next_id = 1
        else:
            # If no file exists, start fresh
            self.tasks = []
            self.next_id = 1