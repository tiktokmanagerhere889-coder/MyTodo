#!/usr/bin/env python3
"""
Professional CLI Task Manager - Main Menu
A user-friendly task manager with a menu-based interface
"""

import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich import print
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
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


class TaskManager:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks: List[Task] = []
        self.next_id = 1
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Convert tasks from the file format to the correct Task model
                self.tasks = []
                for task_data in data.get('tasks', []):
                    # Handle both formats (from main app and from this file)
                    if 'title' in task_data:
                        # Format from main app
                        title = task_data['title']
                        description = task_data.get('description', '')
                        completed = task_data.get('completed', False)
                        date_str = task_data.get('created_at', task_data.get('date_added', datetime.now().strftime("%Y-%m-%d")))
                    else:
                        # Legacy format from this file
                        # Parse description field which might be in "Title: Description" format
                        full_description = task_data.get('description', '')
                        if ': ' in full_description:
                            title, description = full_description.split(': ', 1)
                        else:
                            title = full_description
                            description = ''

                        completed = task_data.get('status') == 'Complete'
                        date_str = task_data.get('date_added', datetime.now().strftime("%Y-%m-%d"))

                    # Convert date string to datetime object
                    try:
                        created_at = datetime.strptime(date_str, "%Y-%m-%d")
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
                        title=title,
                        description=description,
                        completed=completed,
                        created_at=created_at,
                        priority=priority,
                        tags=task_data.get('tags', []),
                        due_date=due_date,
                        is_recurring=task_data.get('is_recurring', False),
                        recurrence_pattern=task_data.get('recurrence_pattern', None)
                    )
                    self.tasks.append(task)

                self.next_id = data.get('next_id', max([task.id for task in self.tasks], default=0) + 1)
            except (json.JSONDecodeError, KeyError, ValueError):
                # If file is corrupted, start fresh
                self.tasks = []
                self.next_id = 1
        else:
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

    def save_tasks(self):
        """Save tasks to JSON file"""
        # Prepare tasks for saving in the required format
        task_list = []
        for task in self.tasks:
            task_dict = {
                'id': task.id,
                'title': task.title,
                'description': task.description or '',
                'completed': task.completed,
                'created_at': task.created_at.strftime('%Y-%m-%d') if task.created_at else datetime.now().strftime('%Y-%m-%d'),
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
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def add_task(self, title: str, description: str = None, priority=None, tags: list = None, due_date=None) -> bool:
        """Add a new task"""
        from datetime import datetime

        if not title.strip():
            return False

        # Use default priority if not specified
        if priority is None:
            priority = Priority.MEDIUM

        task = Task(
            id=self.next_id,
            title=title.strip(),
            description=description,
            completed=False,
            created_at=datetime.now(),
            priority=priority,
            tags=tags or [],
            due_date=due_date
        )
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return True

    def update_task(self, task_id: int, new_title: str = None, new_description: str = None,
                    priority=None, tags: list = None, due_date=None) -> bool:
        """Update a task's title, description, priority, tags, and/or due date"""
        for task in self.tasks:
            if task.id == task_id:
                if new_title is not None:
                    task.title = new_title.strip()
                if new_description is not None:
                    task.description = new_description
                if priority is not None:
                    task.priority = priority
                if tags is not None:
                    task.tags = tags
                if due_date is not None:
                    task.due_date = due_date
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                self.save_tasks()
                return True
        return False

    def add_imported_task(self, task: 'Task') -> bool:
        """Add a task that was imported from a file"""
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

    def mark_complete(self, task_id: int) -> bool:
        """Mark a task as complete"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                self.save_tasks()
                return True
        return False

    def mark_incomplete(self, task_id: int) -> bool:
        """Mark a task as incomplete"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = False
                self.save_tasks()
                return True
        return False

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by its ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return self.tasks


class MainMenuApp:
    def __init__(self):
        self.console = Console()
        self.task_manager = TaskManager()
        self.current_selection = 0
        self.menu_options = [
            "Add Task",
            "Update Task",
            "Delete Task",
            "View Task List",
            "Mark as Complete",
            "Filter Tasks",
            "Sort Tasks",
            "Check Due Tasks",
            "Export Tasks",
            "Import Tasks",
            "Search Tasks",
            "Task Statistics",
            "Exit"
        ]

    def display_menu(self):
        """Display the main menu with current selection highlighted"""
        self.console.clear()

        # Create a large, prominent header for "Console App" with red accent
        from rich.text import Text

        # Create the main header with red prominence
        header_text = Text(justify="center")
        header_text.append("╔════════════════════════════════════════════════════════════════════╗\n", style="bold bright_red")
        header_text.append("║                           ", style="bold bright_red")
        header_text.append("🚀 ", style="bold bright_red")
        header_text.append("C", style="bold bright_red")
        header_text.append("O", style="bold bright_yellow")
        header_text.append("N", style="bold bright_green")
        header_text.append("S", style="bold bright_cyan")
        header_text.append("O", style="bold bright_blue")
        header_text.append("L", style="bold bright_magenta")
        header_text.append("E", style="bold bright_white")
        header_text.append(" ", style="bold bright_red")
        header_text.append("A", style="bold bright_yellow")
        header_text.append("P", style="bold bright_green")
        header_text.append("P", style="bold bright_cyan")
        header_text.append(" ", style="bold bright_blue")
        header_text.append(" ", style="bold bright_magenta")
        header_text.append(" ", style="bold bright_white")
        header_text.append(" ", style="bold bright_red")
        header_text.append("🚀", style="bold bright_red")
        header_text.append("                           ║\n", style="bold bright_red")
        header_text.append("║                      ", style="bold bright_red")
        header_text.append("Professional Task Manager", style="bold italic white")
        header_text.append("                      ║\n", style="bold bright_red")
        header_text.append("╚════════════════════════════════════════════════════════════════════╝", style="bold bright_red")

        self.console.print()
        self.console.print(header_text)
        self.console.print()

        # Calculate and display task statistics with enhanced formatting
        all_tasks = self.task_manager.get_all_tasks()
        total_tasks = len(all_tasks)
        completed_tasks = len([task for task in all_tasks if task.completed])
        pending_tasks = total_tasks - completed_tasks

        # Calculate additional statistics for new features
        high_priority_tasks = len([task for task in all_tasks if task.priority.value == 'high'])
        medium_priority_tasks = len([task for task in all_tasks if task.priority.value == 'medium'])
        low_priority_tasks = len([task for task in all_tasks if task.priority.value == 'low'])

        recurring_tasks = len([task for task in all_tasks if task.is_recurring])

        # Find due tasks
        import datetime
        today = datetime.date.today()
        overdue_tasks = len([task for task in all_tasks
                            if task.due_date and not task.completed
                            and task.due_date.date() < today])
        due_today_tasks = len([task for task in all_tasks
                              if task.due_date and not task.completed
                              and task.due_date.date() == today])

        # Create a progress bar visualization
        if total_tasks > 0:
            completion_percentage = (completed_tasks / total_tasks) * 100
            completed_blocks = int(completion_percentage // 5)  # 20 blocks for 100%
            progress_bar = "█" * completed_blocks + "░" * (20 - completed_blocks)
            progress_text_value = f"[{progress_bar}] {completion_percentage:.1f}%"
        else:
            progress_text_value = "[░░░░░░░░░░░░░░░░░░░░] 0.0%"

        # Display statistics with enhanced formatting
        stats_text = Text()
        stats_text.append("📊 ", style="bold bright_yellow")
        stats_text.append(f"Total: {total_tasks} | ", style="bold white")
        stats_text.append(f"Completed: {completed_tasks} | ", style="bold bright_green")
        stats_text.append(f"Pending: {pending_tasks}", style="bold bright_red")

        progress_text_obj = Text(f"📈 Progress: {progress_text_value}", style="bold bright_magenta")

        # Additional stats for new features
        features_text = Text()
        features_text.append("🔥 ", style="bold bright_red")
        features_text.append(f"High: {high_priority_tasks} | ", style="bold bright_red")
        features_text.append("🟡 ", style="bold bright_yellow")
        features_text.append(f"Med: {medium_priority_tasks} | ", style="bold bright_yellow")
        features_text.append("🟢 ", style="bold bright_green")
        features_text.append(f"Low: {low_priority_tasks} | ", style="bold bright_green")
        features_text.append(f"🔄: {recurring_tasks}", style="bold bright_cyan")

        due_text = Text()
        if overdue_tasks > 0:
            due_text.append(" ⚠️ ", style="bold bright_red")
            due_text.append(f"Overdue: {overdue_tasks} | ", style="bold bright_red")
        due_text.append(" 📅 ", style="bold bright_yellow")
        due_text.append(f"Due Today: {due_today_tasks}", style="bold bright_yellow")

        self.console.print(stats_text)
        self.console.print(progress_text_obj)
        self.console.print(features_text)
        if overdue_tasks > 0 or due_today_tasks > 0:
            self.console.print(due_text)
        self.console.print()

        # Display menu options with numbered selection and enhanced highlighting
        for i, option in enumerate(self.menu_options, 1):  # Start numbering from 1
            if i-1 == self.current_selection:  # Adjust for 0-indexed selection
                # Add number and emoji to the selected option for better visual feedback
                if option == "Add Task":
                    self.console.print(f"[bold black on bright_green] {i}. 📝 {option} [/bold black on bright_green]")
                elif option == "Update Task":
                    self.console.print(f"[bold black on bright_yellow] {i}. ✏️ {option} [/bold black on bright_yellow]")
                elif option == "Delete Task":
                    self.console.print(f"[bold black on bright_red] {i}. 🗑️ {option} [/bold black on bright_red]")
                elif option == "View Task List":
                    self.console.print(f"[bold black on bright_blue] {i}. 📋 {option} [/bold black on bright_blue]")
                elif option == "Mark as Complete":
                    self.console.print(f"[bold black on bright_cyan] {i}. ✅ {option} [/bold black on bright_cyan]")
                elif option == "Export Tasks":
                    self.console.print(f"[bold black on bright_magenta] {i}. 📤 {option} [/bold black on bright_magenta]")
                elif option == "Import Tasks":
                    self.console.print(f"[bold black on bright_cyan] {i}. 📥 {option} [/bold black on bright_cyan]")
                elif option == "Search Tasks":
                    self.console.print(f"[bold black on bright_yellow] {i}. 🔍 {option} [/bold black on bright_yellow]")
                elif option == "Task Statistics":
                    self.console.print(f"[bold black on bright_green] {i}. 📊 {option} [/bold black on bright_green]")
                else:  # Exit
                    self.console.print(f"[bold black on bright_white] {i}. ❌ {option} [/bold black on bright_white]")
            else:
                # Add numbers and appropriate emojis to unselected options
                if option == "Add Task":
                    self.console.print(f"   {i}. 📝 {option}")
                elif option == "Update Task":
                    self.console.print(f"   {i}. ✏️ {option}")
                elif option == "Delete Task":
                    self.console.print(f"   {i}. 🗑️ {option}")
                elif option == "View Task List":
                    self.console.print(f"   {i}. 📋 {option}")
                elif option == "Mark as Complete":
                    self.console.print(f"   {i}. ✅ {option}")
                elif option == "Export Tasks":
                    self.console.print(f"   {i}. 📤 {option}")
                elif option == "Import Tasks":
                    self.console.print(f"   {i}. 📥 {option}")
                elif option == "Search Tasks":
                    self.console.print(f"   {i}. 🔍 {option}")
                elif option == "Task Statistics":
                    self.console.print(f"   {i}. 📊 {option}")
                else:  # Exit
                    self.console.print(f"   {i}. ❌ {option}")

        self.console.print()

    def display_task_list(self):
        """Display all tasks in a table format"""
        self.console.clear()

        tasks = self.task_manager.get_all_tasks()

        header_text = Text("📋 CONSOLE APP - TASK LIST 📋", style="bold bright_cyan on black")
        header = Panel(header_text, expand=False, border_style="bright_cyan", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        if not tasks:
            self.console.print("[bold bright_yellow]📭 No tasks available.[/bold bright_yellow]")
            input("\nPress Enter to return to main menu...")
            return

        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([task for task in tasks if task.completed])
        pending_tasks = total_tasks - completed_tasks
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Create a progress bar visualization
        if total_tasks > 0:
            completed_blocks = int(completion_rate // 5)  # 20 blocks for 100%
            progress_bar = "█" * completed_blocks + "░" * (20 - completed_blocks)
            progress_text_value = f"[{progress_bar}] {completion_rate:.1f}%"
        else:
            progress_text_value = "[░░░░░░░░░░░░░░░░░░░░] 0.0%"

        # Display statistics with enhanced formatting
        stats_text = Text()
        stats_text.append("📊 ", style="bold bright_yellow")
        stats_text.append(f"Total: {total_tasks} | ", style="bold white")
        stats_text.append(f"Completed: {completed_tasks} | ", style="bold bright_green")
        stats_text.append(f"Pending: {pending_tasks}", style="bold bright_red")

        progress_text_obj = Text(f"📈 Progress: {progress_text_value}", style="bold bright_magenta")

        self.console.print(stats_text)
        self.console.print(progress_text_obj)
        self.console.print()

        # Sort tasks: completed first, then by ID
        sorted_tasks = sorted(tasks, key=lambda t: (not t.completed, t.id))

        table = Table(title="All Tasks", show_header=True, header_style="bold bright_magenta")
        table.add_column("#", style="bold bright_yellow", width=3)  # Row number
        table.add_column("ID", style="bold bright_green", width=5)
        table.add_column("Title", style="white", width=20)
        table.add_column("Description", style="white", width=20)
        table.add_column("Status", style="white", width=10)
        table.add_column("Priority", style="white", width=10)
        table.add_column("Due Date", style="white", width=12)
        table.add_column("Tags", style="white", width=15)
        table.add_column("Date Added", style="white", width=12)

        # Add row numbers for easy selection
        for idx, task in enumerate(sorted_tasks, 1):
            status_style = "bold bright_green" if task.completed else "bold bright_red"
            status_text = "Complete" if task.completed else "Pending"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task.priority.value]
            priority_text = f"{priority_emoji} {task.priority.value.title()}"
            due_date_text = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'
            tags_text = ', '.join(task.tags) if task.tags else 'None'

            table.add_row(
                str(idx),  # Row number
                str(task.id),
                task.title,
                task.description or "",
                f"[{status_style}]{status_text}[/{status_style}]",
                f"[{status_style}]{priority_text}[/{status_style}]",
                due_date_text,
                tags_text,
                task.created_at.strftime('%Y-%m-%d') if task.created_at else ''
            )

        self.console.print(table)

        self.console.print("\n[bold bright_cyan]💡 Tip: Use row number (#) for quick selection in other operations[/bold bright_cyan]")
        input("\nPress Enter to return to main menu...")

    def add_task_flow(self):
        """Handle the add task flow"""
        self.console.clear()

        header_text = Text("📝 ADD NEW TASK 📝", style="bold bright_green on black")
        header = Panel(header_text, expand=False, border_style="bright_green", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        title = input("📝 Enter task title: ")
        description = input("📝 Enter task description: ")

        # Get priority
        priority_input = input("📝 Enter priority (high/medium/low) [default: medium]: ").strip().lower()
        if priority_input in ['high', 'medium', 'low']:
            from .models.task import Priority
            if priority_input == 'high':
                priority = Priority.HIGH
            elif priority_input == 'low':
                priority = Priority.LOW
            else:
                priority = Priority.MEDIUM
        else:
            from .models.task import Priority
            priority = Priority.MEDIUM  # default

        # Get tags
        tags_input = input("📝 Enter tags (comma-separated) [optional]: ").strip()
        tags = [tag.strip() for tag in tags_input.split(',')] if tags_input else []

        # Get due date
        due_date_input = input("📝 Enter due date (YYYY-MM-DD) [optional]: ").strip()
        due_date = None
        if due_date_input:
            try:
                from datetime import datetime
                due_date = datetime.strptime(due_date_input, "%Y-%m-%d")
            except ValueError:
                self.console.print("\n[bold bright_yellow]⚠️ Invalid date format. Task will be added without due date.[/bold bright_yellow]")
                due_date = None

        if self.task_manager.add_task(title, description if description else None, priority=priority, tags=tags, due_date=due_date):
            self.console.print("\n[bold bright_green]✅ Task added successfully![/bold bright_green]")
        else:
            self.console.print("\n[bold bright_red]❌ Error: Task title cannot be empty.[/bold bright_red]")

        input("\nPress Enter to return to main menu...")

    def update_task_flow(self):
        """Handle the update task flow"""
        self.console.clear()

        header_text = Text("✏️ UPDATE TASK ✏️", style="bold bright_yellow on black")
        header = Panel(header_text, expand=False, border_style="bright_yellow", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        # Show task list to help user identify task
        tasks = self.task_manager.get_all_tasks()
        if not tasks:
            self.console.print("[bold bright_yellow]No tasks available to update.[/bold bright_yellow]")
            input("\nPress Enter to return to main menu...")
            return

        # Display tasks with row numbers
        table = Table(title="Current Tasks", show_header=True, header_style="bold bright_magenta")
        table.add_column("#", style="bold bright_yellow", width=3)  # Row number
        table.add_column("ID", style="bold bright_green", width=5)
        table.add_column("Title", style="white", width=25)
        table.add_column("Description", style="white", width=25)
        table.add_column("Status", style="white", width=12)

        sorted_tasks = sorted(tasks, key=lambda t: (not t.completed, t.id))
        task_map = {}  # Map row numbers to task IDs

        for idx, task in enumerate(sorted_tasks, 1):
            status_style = "bold bright_green" if task.completed else "bold bright_red"
            status_text = "Complete" if task.completed else "Pending"
            table.add_row(
                str(idx),  # Row number
                str(task.id),
                task.title,
                task.description or "",
                f"[{status_style}]{status_text}[/{status_style}]"
            )
            task_map[idx] = task.id  # Map row number to actual task ID

        self.console.print(table)
        self.console.print()

        selection = input("Enter Task ROW NUMBER or ID to update: ").strip()

        # Determine if user entered a row number or task ID
        if selection.isdigit():
            selection_num = int(selection)
            if selection_num in task_map:
                task_id = task_map[selection_num]  # Convert row number to task ID
            else:
                task_id = selection_num  # User entered actual task ID
        else:
            self.console.print("\n[bold bright_red]❌ Error: Invalid input. Please enter a number.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            self.console.print(f"\n[bold bright_red]❌ Error: Task with ID {task_id} not found.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        new_title = input(f"📝 Enter new title (current: {task.title}): ") or task.title
        new_description = input(f"📝 Enter new description (current: {task.description or ''}): ")
        if new_description == "":  # If user pressed Enter without typing
            new_description = task.description

        # Get new priority
        priority_input = input(f"📝 Enter new priority (high/medium/low) [current: {task.priority.value}, press Enter to keep current]: ").strip().lower()
        if priority_input in ['high', 'medium', 'low']:
            from .models.task import Priority
            if priority_input == 'high':
                new_priority = Priority.HIGH
            elif priority_input == 'low':
                new_priority = Priority.LOW
            else:
                new_priority = Priority.MEDIUM
        elif priority_input == "":
            new_priority = task.priority  # Keep current priority
        else:
            self.console.print(f"\n[bold bright_yellow]⚠️ Invalid priority. Keeping current priority: {task.priority.value}[/bold bright_yellow]")
            new_priority = task.priority

        # Get new tags
        tags_input = input(f"📝 Enter new tags (comma-separated) [current: {', '.join(task.tags) if task.tags else 'none'}, press Enter to keep current]: ").strip()
        if tags_input:
            new_tags = [tag.strip() for tag in tags_input.split(',')]
        elif tags_input == "":  # User pressed Enter to keep current
            new_tags = task.tags
        else:
            new_tags = []

        # Get new due date
        due_date_input = input(f"📝 Enter new due date (YYYY-MM-DD) [current: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'none'}, press Enter to keep current]: ").strip()
        if due_date_input:
            try:
                from datetime import datetime
                new_due_date = datetime.strptime(due_date_input, "%Y-%m-%d")
            except ValueError:
                self.console.print("\n[bold bright_yellow]⚠️ Invalid date format. Keeping current due date.[/bold bright_yellow]")
                new_due_date = task.due_date
        elif due_date_input == "":  # User pressed Enter to keep current
            new_due_date = task.due_date
        else:
            new_due_date = None

        if self.task_manager.update_task(task_id, new_title, new_description, priority=new_priority, tags=new_tags, due_date=new_due_date):
            self.console.print(f"\n[bold bright_green]✅ Task {task_id} updated successfully![/bold bright_green]")
        else:
            self.console.print(f"\n[bold bright_red]❌ Error: Failed to update task {task_id}.[/bold bright_red]")

        input("\nPress Enter to return to main menu...")

    def delete_task_flow(self):
        """Handle the delete task flow"""
        self.console.clear()

        header_text = Text("🗑️ DELETE TASK 🗑️", style="bold bright_red on black")
        header = Panel(header_text, expand=False, border_style="bright_red", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        # Show task list to help user identify task
        tasks = self.task_manager.get_all_tasks()
        if not tasks:
            self.console.print("[bold bright_yellow]No tasks available to delete.[/bold bright_yellow]")
            input("\nPress Enter to return to main menu...")
            return

        # Display tasks with row numbers
        table = Table(title="Current Tasks", show_header=True, header_style="bold bright_magenta")
        table.add_column("#", style="bold bright_yellow", width=3)  # Row number
        table.add_column("ID", style="bold bright_green", width=5)
        table.add_column("Title", style="white", width=25)
        table.add_column("Description", style="white", width=25)
        table.add_column("Status", style="white", width=12)

        sorted_tasks = sorted(tasks, key=lambda t: (not t.completed, t.id))
        task_map = {}  # Map row numbers to task IDs

        for idx, task in enumerate(sorted_tasks, 1):
            status_style = "bold bright_green" if task.completed else "bold bright_red"
            status_text = "Complete" if task.completed else "Pending"
            table.add_row(
                str(idx),  # Row number
                str(task.id),
                task.title,
                task.description or "",
                f"[{status_style}]{status_text}[/{status_style}]"
            )
            task_map[idx] = task.id  # Map row number to actual task ID

        self.console.print(table)
        self.console.print()

        selection = input("Enter Task ROW NUMBER or ID to delete: ").strip()

        # Determine if user entered a row number or task ID
        if selection.isdigit():
            selection_num = int(selection)
            if selection_num in task_map:
                task_id = task_map[selection_num]  # Convert row number to task ID
            else:
                task_id = selection_num  # User entered actual task ID
        else:
            self.console.print("\n[bold bright_red]❌ Error: Invalid input. Please enter a number.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            self.console.print(f"\n[bold bright_red]❌ Error: Task with ID {task_id} not found.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        confirm = input(f"❓ Are you sure you want to delete task '{task.title}'? (y/n): ").lower()

        if confirm in ['y', 'yes']:
            if self.task_manager.delete_task(task_id):
                self.console.print(f"\n[bold bright_green]✅ Task {task_id} deleted successfully![/bold bright_green]")
            else:
                self.console.print(f"\n[bold bright_red]❌ Error: Failed to delete task {task_id}.[/bold bright_red]")
        else:
            self.console.print("\n[bold bright_yellow]⚠️ Deletion cancelled.[/bold bright_yellow]")

        input("\nPress Enter to return to main menu...")

    def mark_complete_flow(self):
        """Handle the mark as complete flow"""
        self.console.clear()

        header_text = Text("✅ MARK TASK COMPLETE ✅", style="bold bright_cyan on black")
        header = Panel(header_text, expand=False, border_style="bright_cyan", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        # Show task list to help user identify task
        tasks = self.task_manager.get_all_tasks()
        if not tasks:
            self.console.print("[bold bright_yellow]No tasks available to mark as complete.[/bold bright_yellow]")
            input("\nPress Enter to return to main menu...")
            return

        # Display tasks with row numbers
        table = Table(title="Current Tasks", show_header=True, header_style="bold bright_magenta")
        table.add_column("#", style="bold bright_yellow", width=3)  # Row number
        table.add_column("ID", style="bold bright_green", width=5)
        table.add_column("Title", style="white", width=25)
        table.add_column("Description", style="white", width=25)
        table.add_column("Status", style="white", width=12)

        sorted_tasks = sorted(tasks, key=lambda t: (not t.completed, t.id))
        task_map = {}  # Map row numbers to task IDs

        for idx, task in enumerate(sorted_tasks, 1):
            status_style = "bold bright_green" if task.completed else "bold bright_red"
            status_text = "Complete" if task.completed else "Pending"
            table.add_row(
                str(idx),  # Row number
                str(task.id),
                task.title,
                task.description or "",
                f"[{status_style}]{status_text}[/{status_style}]"
            )
            task_map[idx] = task.id  # Map row number to actual task ID

        self.console.print(table)
        self.console.print()

        selection = input("Enter Task ROW NUMBER or ID to mark as complete: ").strip()

        # Determine if user entered a row number or task ID
        if selection.isdigit():
            selection_num = int(selection)
            if selection_num in task_map:
                task_id = task_map[selection_num]  # Convert row number to task ID
            else:
                task_id = selection_num  # User entered actual task ID
        else:
            self.console.print("\n[bold bright_red]❌ Error: Invalid input. Please enter a number.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            self.console.print(f"\n[bold bright_red]❌ Error: Task with ID {task_id} not found.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        if self.task_manager.mark_complete(task_id):
            self.console.print(f"\n[bold bright_green]✅ Task {task_id} marked as complete![/bold bright_green]")
        else:
            self.console.print(f"\n[bold bright_red]❌ Error: Failed to mark task {task_id} as complete.[/bold bright_red]")

        input("\nPress Enter to return to main menu...")

    def export_tasks_flow(self):
        """Export tasks to a JSON file"""
        self.console.clear()

        header_text = Text("📤 EXPORT TASKS 📤", style="bold bright_magenta on black")
        header = Panel(header_text, expand=False, border_style="bright_magenta", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        filename = input("Enter filename to export tasks (default: tasks_export.json): ").strip()
        if not filename:
            filename = "tasks_export.json"

        try:
            tasks = self.task_manager.get_all_tasks()
            if not tasks:
                self.console.print("[bold bright_yellow]No tasks to export.[/bold bright_yellow]")
            else:
                # Prepare tasks for export
                export_data = {
                    'tasks': [
                        {
                            'id': task.id,
                            'title': task.title,
                            'description': task.description or '',
                            'completed': task.completed,
                            'created_at': task.created_at.strftime('%Y-%m-%d') if task.created_at else datetime.now().strftime('%Y-%m-%d')
                        } for task in tasks
                    ]
                }

                with open(filename, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(export_data, f, indent=2)

                self.console.print(f"[bold bright_green]✅ Successfully exported {len(tasks)} tasks to {filename}[/bold bright_green]")
        except Exception as e:
            self.console.print(f"[bold bright_red]❌ Error exporting tasks: {str(e)}[/bold bright_red]")

        input("\nPress Enter to return to main menu...")

    def import_tasks_flow(self):
        """Import tasks from a JSON file"""
        self.console.clear()

        header_text = Text("📥 IMPORT TASKS 📥", style="bold bright_magenta on black")
        header = Panel(header_text, expand=False, border_style="bright_magenta", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        filename = input("Enter filename to import tasks from: ").strip()
        if not filename:
            self.console.print("[bold bright_red]❌ No filename provided.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)

            if 'tasks' in data:
                imported_count = 0
                for task_data in data['tasks']:
                    # Convert date string to datetime object
                    try:
                        created_at = datetime.strptime(task_data.get('created_at', datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
                    except ValueError:
                        created_at = datetime.now()

                    # Create a new task with current ID but add to task manager
                    new_task = Task(
                        id=task_data['id'],
                        title=task_data.get('title', ''),
                        description=task_data.get('description', ''),
                        completed=task_data.get('completed', False),
                        created_at=created_at
                    )
                    # Add to task manager
                    if self.task_manager.add_imported_task(new_task):
                        imported_count += 1

                self.console.print(f"[bold bright_green]✅ Successfully imported {imported_count} tasks from {filename}[/bold bright_green]")
            else:
                self.console.print("[bold bright_red]❌ Invalid file format: no 'tasks' key found.[/bold bright_red]")
        except FileNotFoundError:
            self.console.print(f"[bold bright_red]❌ File {filename} not found.[/bold bright_red]")
        except Exception as e:
            self.console.print(f"[bold bright_red]❌ Error importing tasks: {str(e)}[/bold bright_red]")

        input("\nPress Enter to return to main menu...")

    def search_tasks_flow(self):
        """Search tasks by title, description, or ID"""
        self.console.clear()

        header_text = Text("🔍 SEARCH TASKS 🔍", style="bold bright_magenta on black")
        header = Panel(header_text, expand=False, border_style="bright_magenta", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        search_term = input("Enter search term (or ID): ").strip()
        if not search_term:
            self.console.print("[bold bright_yellow]No search term provided.[/bold bright_yellow]")
            input("\nPress Enter to return to main menu...")
            return

        # Use the new search_tasks method which searches in title and description
        tasks = self.task_manager.search_tasks(search_term)

        if tasks:
            self.console.print(f"[bold bright_green]Found {len(tasks)} matching task(s):[/bold bright_green]")
            self.console.print()

            table = Table(title="Search Results", show_header=True, header_style="bold bright_magenta")
            table.add_column("ID", style="bold bright_green", width=5)
            table.add_column("Title", style="white", width=20)
            table.add_column("Description", style="white", width=20)
            table.add_column("Status", style="white", width=10)
            table.add_column("Priority", style="white", width=10)
            table.add_column("Due Date", style="white", width=12)
            table.add_column("Tags", style="white", width=15)
            table.add_column("Date Added", style="white", width=12)

            for task in tasks:
                status_style = "bold bright_green" if task.completed else "bold bright_red"
                status_text = "Complete" if task.completed else "Pending"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task.priority.value]
                priority_text = f"{priority_emoji} {task.priority.value.title()}"
                due_date_text = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'
                tags_text = ', '.join(task.tags) if task.tags else 'None'

                table.add_row(
                    str(task.id),
                    task.title,
                    task.description or "",
                    f"[{status_style}]{status_text}[/{status_style}]",
                    f"[{status_style}]{priority_text}[/{status_style}]",
                    due_date_text,
                    tags_text,
                    task.created_at.strftime('%Y-%m-%d') if task.created_at else ''
                )

            self.console.print(table)
        else:
            self.console.print("[bold bright_yellow]No tasks found matching your search.[/bold bright_yellow]")

        input("\nPress Enter to return to main menu...")

    def filter_tasks_flow(self):
        """Filter tasks by status, priority, or tag"""
        self.console.clear()

        header_text = Text("🔍 FILTER TASKS 🔍", style="bold bright_magenta on black")
        header = Panel(header_text, expand=False, border_style="bright_magenta", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        # Get filter criteria from user
        status_input = input("Enter status to filter (completed/incomplete) [optional]: ").strip().lower()
        if status_input in ['completed', 'complete', 'done']:
            status = True
        elif status_input in ['incomplete', 'pending', 'todo']:
            status = False
        elif status_input == "":
            status = None
        else:
            self.console.print(f"\n[bold bright_yellow]⚠️ Invalid status. No status filter will be applied.[/bold bright_yellow]")
            status = None

        priority_input = input("Enter priority to filter (high/medium/low) [optional]: ").strip().lower()
        if priority_input in ['high', 'medium', 'low']:
            from .models.task import Priority
            if priority_input == 'high':
                priority = Priority.HIGH
            elif priority_input == 'low':
                priority = Priority.LOW
            else:
                priority = Priority.MEDIUM
        elif priority_input == "":
            priority = None
        else:
            self.console.print(f"\n[bold bright_yellow]⚠️ Invalid priority. No priority filter will be applied.[/bold bright_yellow]")
            priority = None

        tag_input = input("Enter tag to filter [optional]: ").strip()
        if tag_input == "":
            tag = None
        else:
            tag = tag_input

        # Apply filters
        tasks = self.task_manager.filter_tasks(status=status, priority=priority, tag=tag)

        if tasks:
            self.console.print(f"\n[bold bright_green]Found {len(tasks)} filtered task(s):[/bold bright_green]")
            self.console.print()

            table = Table(title="Filtered Tasks", show_header=True, header_style="bold bright_magenta")
            table.add_column("#", style="bold bright_yellow", width=3)  # Row number
            table.add_column("ID", style="bold bright_green", width=5)
            table.add_column("Title", style="white", width=20)
            table.add_column("Description", style="white", width=20)
            table.add_column("Status", style="white", width=10)
            table.add_column("Priority", style="white", width=10)
            table.add_column("Due Date", style="white", width=12)
            table.add_column("Tags", style="white", width=15)
            table.add_column("Date Added", style="white", width=12)

            # Add row numbers for easy selection
            for idx, task in enumerate(tasks, 1):  # Using the filtered tasks directly
                status_style = "bold bright_green" if task.completed else "bold bright_red"
                status_text = "Complete" if task.completed else "Pending"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task.priority.value]
                priority_text = f"{priority_emoji} {task.priority.value.title()}"
                due_date_text = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'
                tags_text = ', '.join(task.tags) if task.tags else 'None'

                table.add_row(
                    str(idx),  # Row number
                    str(task.id),
                    task.title,
                    task.description or "",
                    f"[{status_style}]{status_text}[/{status_style}]",
                    f"[{status_style}]{priority_text}[/{status_style}]",
                    due_date_text,
                    tags_text,
                    task.created_at.strftime('%Y-%m-%d') if task.created_at else ''
                )

            self.console.print(table)
        else:
            self.console.print("\n[bold bright_yellow]No tasks found matching the filter criteria.[/bold bright_yellow]")

        input("\nPress Enter to return to main menu...")

    def sort_tasks_flow(self):
        """Sort tasks by various criteria"""
        self.console.clear()

        header_text = Text("📊 SORT TASKS 📊", style="bold bright_magenta on black")
        header = Panel(header_text, expand=False, border_style="bright_magenta", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        # Get sort criteria from user
        print("Sort options: id, title, date, priority, due_date")
        by_input = input("Enter sort criteria [default: id]: ").strip().lower()
        if by_input in ['id', 'title', 'date', 'priority', 'due_date']:
            by = by_input
            if by == 'date':
                by = 'created_at'  # map 'date' to 'created_at'
        elif by_input == "":
            by = 'id'  # default
        else:
            self.console.print(f"\n[bold bright_yellow]⚠️ Invalid sort option. Using default (id).[/bold bright_yellow]")
            by = 'id'

        order_input = input("Enter sort order (asc/desc) [default: asc]: ").strip().lower()
        if order_input in ['desc', 'descending', 'reverse']:
            reverse = True
        elif order_input in ['asc', 'ascending', '']:
            reverse = False  # default
        else:
            self.console.print(f"\n[bold bright_yellow]⚠️ Invalid order. Using ascending order.[/bold bright_yellow]")
            reverse = False

        # Apply sorting
        tasks = self.task_manager.sort_tasks(by=by, reverse=reverse)

        if tasks:
            order_str = "descending" if reverse else "ascending"
            self.console.print(f"\n[bold bright_green]Tasks sorted by {by} ({order_str}):[/bold bright_green]")
            self.console.print()

            table = Table(title=f"Tasks Sorted by {by.title()}", show_header=True, header_style="bold bright_magenta")
            table.add_column("#", style="bold bright_yellow", width=3)  # Row number
            table.add_column("ID", style="bold bright_green", width=5)
            table.add_column("Title", style="white", width=20)
            table.add_column("Description", style="white", width=20)
            table.add_column("Status", style="white", width=10)
            table.add_column("Priority", style="white", width=10)
            table.add_column("Due Date", style="white", width=12)
            table.add_column("Tags", style="white", width=15)
            table.add_column("Date Added", style="white", width=12)

            # Add row numbers for easy selection
            for idx, task in enumerate(tasks, 1):  # Using the sorted tasks
                status_style = "bold bright_green" if task.completed else "bold bright_red"
                status_text = "Complete" if task.completed else "Pending"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task.priority.value]
                priority_text = f"{priority_emoji} {task.priority.value.title()}"
                due_date_text = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'
                tags_text = ', '.join(task.tags) if task.tags else 'None'

                table.add_row(
                    str(idx),  # Row number
                    str(task.id),
                    task.title,
                    task.description or "",
                    f"[{status_style}]{status_text}[/{status_style}]",
                    f"[{status_style}]{priority_text}[/{status_style}]",
                    due_date_text,
                    tags_text,
                    task.created_at.strftime('%Y-%m-%d') if task.created_at else ''
                )

            self.console.print(table)
        else:
            self.console.print("\n[bold bright_yellow]No tasks to display.[/bold bright_yellow]")

        input("\nPress Enter to return to main menu...")

    def check_due_tasks_flow(self):
        """Check and display tasks that are due today or overdue"""
        self.console.clear()

        header_text = Text("📅 CHECK DUE TASKS 📅", style="bold bright_magenta on black")
        header = Panel(header_text, expand=False, border_style="bright_magenta", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        import datetime
        today = datetime.date.today()

        # Find tasks that are due today or overdue
        due_tasks = []
        overdue_tasks = []

        for task in self.task_manager.get_all_tasks():
            if task.due_date and not task.completed:
                due_date = task.due_date.date() if isinstance(task.due_date, datetime.datetime) else task.due_date

                if due_date < today:
                    overdue_tasks.append(task)
                elif due_date == today:
                    due_tasks.append(task)

        if overdue_tasks:
            self.console.print(f"\n[bold bright_red]⚠️ {len(overdue_tasks)} OVERDUE TASK(S):[/bold bright_red]")
            self.console.print()

            table = Table(title="Overdue Tasks", show_header=True, header_style="bold bright_red")
            table.add_column("ID", style="bold bright_red", width=5)
            table.add_column("Title", style="white", width=25)
            table.add_column("Description", style="white", width=25)
            table.add_column("Priority", style="white", width=10)
            table.add_column("Due Date", style="white", width=12)
            table.add_column("Tags", style="white", width=15)

            for task in overdue_tasks:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task.priority.value]
                priority_text = f"{priority_emoji} {task.priority.value.title()}"
                due_date_text = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'
                tags_text = ', '.join(task.tags) if task.tags else 'None'

                table.add_row(
                    str(task.id),
                    task.title,
                    task.description or "",
                    f"[bold bright_red]{priority_text}[/bold bright_red]",
                    f"[bold bright_red]{due_date_text}[/bold bright_red]",
                    tags_text
                )

            self.console.print(table)
            self.console.print()

        if due_tasks:
            self.console.print(f"\n[bold bright_yellow]📅 {len(due_tasks)} TASK(S) DUE TODAY:[/bold bright_yellow]")
            self.console.print()

            table = Table(title="Tasks Due Today", show_header=True, header_style="bold bright_yellow")
            table.add_column("ID", style="bold bright_yellow", width=5)
            table.add_column("Title", style="white", width=25)
            table.add_column("Description", style="white", width=25)
            table.add_column("Priority", style="white", width=10)
            table.add_column("Due Date", style="white", width=12)
            table.add_column("Tags", style="white", width=15)

            for task in due_tasks:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task.priority.value]
                priority_text = f"{priority_emoji} {task.priority.value.title()}"
                due_date_text = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'
                tags_text = ', '.join(task.tags) if task.tags else 'None'

                table.add_row(
                    str(task.id),
                    task.title,
                    task.description or "",
                    f"[bold bright_yellow]{priority_text}[/bold bright_yellow]",
                    f"[bold bright_yellow]{due_date_text}[/bold bright_yellow]",
                    tags_text
                )

            self.console.print(table)

        if not overdue_tasks and not due_tasks:
            self.console.print("\n[bold bright_green]✅ No tasks are due today or overdue![/bold bright_green]")

        input("\nPress Enter to return to main menu...")

    def task_statistics_flow(self):
        """Display task statistics and analytics"""
        self.console.clear()

        header_text = Text("📊 TASK STATISTICS 📊", style="bold bright_magenta on black")
        header = Panel(header_text, expand=False, border_style="bright_magenta", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        tasks = self.task_manager.get_all_tasks()
        if not tasks:
            self.console.print("[bold bright_yellow]No tasks available for statistics.[/bold bright_yellow]")
            input("\nPress Enter to return to main menu...")
            return

        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([task for task in tasks if task.completed])
        pending_tasks = len([task for task in tasks if not task.completed])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Calculate average days since creation
        from datetime import datetime
        if tasks:
            total_days = 0
            for task in tasks:
                try:
                    task_date = task.created_at
                    days_diff = (datetime.now() - task_date).days
                    total_days += days_diff
                except ValueError:
                    continue
            avg_age = total_days / len(tasks) if tasks else 0
        else:
            avg_age = 0

        # Display statistics
        stats_table = Table(title="Task Statistics", show_header=False, box=None)
        stats_table.add_column("Stat", style="bold bright_cyan", width=20)
        stats_table.add_column("Value", style="white", width=20)

        stats_table.add_row("Total Tasks:", f"[bold white]{total_tasks}[/bold white]")
        stats_table.add_row("Completed Tasks:", f"[bold bright_green]{completed_tasks}[/bold bright_green]")
        stats_table.add_row("Pending Tasks:", f"[bold bright_red]{pending_tasks}[/bold bright_red]")
        stats_table.add_row("Completion Rate:", f"[bold bright_magenta]{completion_rate:.1f}%[/bold bright_magenta]")
        stats_table.add_row("Average Task Age:", f"[bold bright_yellow]{avg_age:.1f} days[/bold bright_yellow]")

        self.console.print(stats_table)

        # Show progress bar
        completed_blocks = int(completion_rate // 5)  # 20 blocks for 100%
        progress_bar = "█" * completed_blocks + "░" * (20 - completed_blocks)
        self.console.print(f"\nProgress: [{progress_bar}] {completion_rate:.1f}%")

        input("\nPress Enter to return to main menu...")

    def run(self):
        """Main application loop with simple input navigation"""
        try:
            while True:
                self.display_menu()

                # Get user input
                try:
                    choice = input("\n[bold bright_cyan]Use W/S to navigate, Enter to select, or enter option number (Q to quit): [/bold bright_cyan]").strip().lower()
                except EOFError:
                    self.console.print("\n[bold bright_cyan]👋 Goodbye! Thanks for using Console App! 👋[/bold bright_cyan]")
                    break

                # Handle navigation and selection
                if choice == 'q':
                    self.console.print("\n[bold bright_cyan]👋 Goodbye! Thanks for using Console App! 👋[/bold bright_cyan]")
                    break
                elif choice == 'w':
                    self.current_selection = (self.current_selection - 1) % len(self.menu_options)
                elif choice == 's':
                    self.current_selection = (self.current_selection + 1) % len(self.menu_options)
                elif choice == '':
                    # Execute the selected option with Enter key
                    selected_option = self.menu_options[self.current_selection]

                    if selected_option == "Add Task":
                        self.add_task_flow()
                    elif selected_option == "Update Task":
                        self.update_task_flow()
                    elif selected_option == "Delete Task":
                        self.delete_task_flow()
                    elif selected_option == "View Task List":
                        self.display_task_list()
                    elif selected_option == "Mark as Complete":
                        self.mark_complete_flow()
                    elif selected_option == "Filter Tasks":
                        self.filter_tasks_flow()
                    elif selected_option == "Sort Tasks":
                        self.sort_tasks_flow()
                    elif selected_option == "Check Due Tasks":
                        self.check_due_tasks_flow()
                    elif selected_option == "Export Tasks":
                        self.export_tasks_flow()
                    elif selected_option == "Import Tasks":
                        self.import_tasks_flow()
                    elif selected_option == "Search Tasks":
                        self.search_tasks_flow()
                    elif selected_option == "Task Statistics":
                        self.task_statistics_flow()
                    elif selected_option == "Exit":
                        self.console.print("\n[bold bright_cyan]👋 Goodbye! Thanks for using Console App! 👋[/bold bright_cyan]")
                        break
                elif choice.isdigit():
                    # Allow direct selection by number
                    option_index = int(choice) - 1
                    if 0 <= option_index < len(self.menu_options):
                        # Set the current selection to the chosen option
                        self.current_selection = option_index
                        selected_option = self.menu_options[self.current_selection]

                        if selected_option == "Add Task":
                            self.add_task_flow()
                        elif selected_option == "Update Task":
                            self.update_task_flow()
                        elif selected_option == "Delete Task":
                            self.delete_task_flow()
                        elif selected_option == "View Task List":
                            self.display_task_list()
                        elif selected_option == "Mark as Complete":
                            self.mark_complete_flow()
                        elif selected_option == "Filter Tasks":
                            self.filter_tasks_flow()
                        elif selected_option == "Sort Tasks":
                            self.sort_tasks_flow()
                        elif selected_option == "Check Due Tasks":
                            self.check_due_tasks_flow()
                        elif selected_option == "Export Tasks":
                            self.export_tasks_flow()
                        elif selected_option == "Import Tasks":
                            self.import_tasks_flow()
                        elif selected_option == "Search Tasks":
                            self.search_tasks_flow()
                        elif selected_option == "Task Statistics":
                            self.task_statistics_flow()
                        elif selected_option == "Exit":
                            self.console.print("\n[bold bright_cyan]👋 Goodbye! Thanks for using Console App! 👋[/bold bright_cyan]")
                            break
        except KeyboardInterrupt:
            self.console.print("\n\n[bold bright_cyan]👋 Goodbye! Thanks for using Console App! 👋[/bold bright_cyan]")


def main():
    app = MainMenuApp()
    app.run()


if __name__ == "__main__":
    main()