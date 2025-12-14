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

    def add_task(self, title: str, description: Optional[str] = None, priority=None, tags: list = None, due_date=None) -> Task:
        """
        Creates and adds a new task to the in-memory list

        Args:
            title (str): The title of the task (required)
            description (str, optional): The description of the task
            priority (Priority, optional): Priority level (low, medium, high)
            tags (list, optional): List of tags for categorization
            due_date (datetime, optional): Due date for the task

        Returns:
            Task: The newly created task object
        """
        from .models.task import Priority

        # Generate unique ID for the task
        task_id = self.next_id
        self.next_id += 1

        # Use default priority if not specified
        if priority is None:
            priority = Priority.MEDIUM

        # Create the new task
        new_task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags or [],
            due_date=due_date
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

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None,
                    priority=None, tags: list = None, due_date=None) -> bool:
        """
        Updates an existing task's title, description, priority, tags, and/or due date

        Args:
            task_id (int): The ID of the task to update
            title (str, optional): New title for the task
            description (str, optional): New description for the task
            priority (Priority, optional): New priority level
            tags (list, optional): New list of tags
            due_date (datetime, optional): New due date

        Returns:
            bool: True if task was updated, False if task not found
        """
        from .models.task import Priority

        task = self.get_task_by_id(task_id)
        if task:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if priority is not None:
                task.priority = priority
            if tags is not None:
                task.tags = tags
            if due_date is not None:
                task.due_date = due_date
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
                'created_at': task.created_at.strftime("%Y-%m-%d") if task.created_at else datetime.now().strftime("%Y-%m-%d"),
                'priority': task.priority.value if hasattr(task, 'priority') else 'medium',
                'tags': task.tags if hasattr(task, 'tags') else [],
                'due_date': task.due_date.strftime("%Y-%m-%d") if hasattr(task, 'due_date') and task.due_date else None,
                'is_recurring': task.is_recurring if hasattr(task, 'is_recurring') else False,
                'recurrence_pattern': task.recurrence_pattern if hasattr(task, 'recurrence_pattern') else None
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
        from .models.task import Priority

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

                    # Handle due date
                    due_date = None
                    if task_data.get('due_date'):
                        try:
                            due_date = datetime.strptime(task_data['due_date'], "%Y-%m-%d")
                        except ValueError:
                            due_date = None

                    # Get priority with fallback to medium
                    priority_str = task_data.get('priority', 'medium')
                    try:
                        priority = Priority(priority_str)
                    except ValueError:
                        priority = Priority.MEDIUM

                    task = Task(
                        id=task_data['id'],
                        title=task_data.get('title', ''),
                        description=task_data.get('description', ''),
                        completed=task_data.get('completed', False),
                        created_at=created_at,
                        priority=priority,
                        tags=task_data.get('tags', []),
                        due_date=due_date,
                        is_recurring=task_data.get('is_recurring', False),
                        recurrence_pattern=task_data.get('recurrence_pattern', None)
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

    def search_tasks(self, query: str) -> List[Task]:
        """
        Search tasks by title or description
        """
        query_lower = query.lower()
        return [
            task for task in self.tasks
            if query_lower in task.title.lower() or
            (task.description and query_lower in task.description.lower())
        ]

    def filter_tasks(self, status: Optional[bool] = None, priority=None, tag: Optional[str] = None) -> List[Task]:
        """
        Filter tasks by status, priority, or tag
        """
        from .models.task import Priority

        filtered_tasks = self.tasks

        if status is not None:
            filtered_tasks = [task for task in filtered_tasks if task.completed == status]

        if priority is not None:
            filtered_tasks = [task for task in filtered_tasks if task.priority == priority]

        if tag is not None:
            filtered_tasks = [task for task in filtered_tasks if tag in task.tags]

        return filtered_tasks

    def sort_tasks(self, by: str = 'id', reverse: bool = False) -> List[Task]:
        """
        Sort tasks by various criteria
        by options: 'id', 'title', 'created_at', 'due_date', 'priority'
        """
        if by == 'id':
            return sorted(self.tasks, key=lambda t: t.id, reverse=reverse)
        elif by == 'title':
            return sorted(self.tasks, key=lambda t: t.title.lower(), reverse=reverse)
        elif by == 'created_at':
            return sorted(self.tasks, key=lambda t: t.created_at, reverse=reverse)
        elif by == 'due_date':
            return sorted(self.tasks, key=lambda t: (t.due_date is None, t.due_date), reverse=reverse)
        elif by == 'priority':
            # Higher priority values should come first
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            return sorted(self.tasks, key=lambda t: priority_order.get(t.priority.value, 0), reverse=reverse)
        else:
            return self.tasks

    def add_recurring_task(self, title: str, description: Optional[str] = None, priority=None,
                          tags: list = None, due_date=None, recurrence_pattern: str = "daily") -> Task:
        """
        Add a recurring task that will automatically create new instances based on the pattern
        """
        from .models.task import Priority
        import datetime

        # Use default priority if not specified
        if priority is None:
            priority = Priority.MEDIUM

        # Create the recurring task
        task_id = self.next_id
        self.next_id += 1

        new_task = Task(
            id=task_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.datetime.now(),
            priority=priority,
            tags=tags or [],
            due_date=due_date,
            is_recurring=True,
            recurrence_pattern=recurrence_pattern
        )

        self.tasks.append(new_task)
        self.save_tasks()
        return new_task

    def check_and_create_recurring_tasks(self):
        """
        Check for recurring tasks and create new instances if needed
        """
        import datetime
        from .models.task import Priority

        today = datetime.date.today()
        new_tasks_created = 0

        for task in self.tasks:
            if task.is_recurring and task.completed:
                # Check if a new instance should be created based on the recurrence pattern
                should_create_new = False

                if task.recurrence_pattern == "daily":
                    should_create_new = True
                elif task.recurrence_pattern == "weekly":
                    # Create a new task if it's been at least a week since the last one
                    if hasattr(task, 'last_occurrence_date'):
                        last_date = task.last_occurrence_date
                    else:
                        last_date = task.created_at.date()
                    if (today - last_date).days >= 7:
                        should_create_new = True
                elif task.recurrence_pattern == "monthly":
                    # Create a new task if it's a new month
                    if hasattr(task, 'last_occurrence_date'):
                        last_date = task.last_occurrence_date
                    else:
                        last_date = task.created_at.date()
                    if (today.year > last_date.year) or (today.month > last_date.month):
                        should_create_new = True
                elif task.recurrence_pattern == "yearly":
                    # Create a new task if it's a new year
                    if hasattr(task, 'last_occurrence_date'):
                        last_date = task.last_occurrence_date
                    else:
                        last_date = task.created_at.date()
                    if today.year > last_date.year:
                        should_create_new = True

                if should_create_new:
                    # Create a new instance of the recurring task
                    new_task_id = self.next_id
                    self.next_id += 1

                    new_task = Task(
                        id=new_task_id,
                        title=task.title,
                        description=task.description,
                        completed=False,
                        created_at=datetime.datetime.now(),
                        priority=task.priority,
                        tags=task.tags,
                        due_date=task.due_date,  # May need to adjust based on recurrence
                        is_recurring=True,
                        recurrence_pattern=task.recurrence_pattern
                    )

                    self.tasks.append(new_task)
                    new_tasks_created += 1

        if new_tasks_created > 0:
            self.save_tasks()

        return new_tasks_created