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


@dataclass
class Task:
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

                    task = Task(
                        id=task_data['id'],
                        title=title,
                        description=description,
                        completed=completed,
                        created_at=created_at
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
                'created_at': task.created_at.strftime('%Y-%m-%d') if task.created_at else datetime.now().strftime('%Y-%m-%d')
            }
            task_list.append(task_dict)

        data = {
            'tasks': task_list,
            'next_id': self.next_id
        }
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def add_task(self, title: str, description: str = None) -> bool:
        """Add a new task"""
        if not title.strip():
            return False

        task = Task(
            id=self.next_id,
            title=title.strip(),
            description=description,
            completed=False,
            created_at=datetime.now()
        )
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return True

    def update_task(self, task_id: int, new_title: str = None, new_description: str = None) -> bool:
        """Update a task's title and/or description"""
        for task in self.tasks:
            if task.id == task_id:
                if new_title is not None:
                    task.title = new_title.strip()
                if new_description is not None:
                    task.description = new_description
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
            "Export Tasks",
            "Import Tasks",
            "Search Tasks",
            "Task Statistics",
            "Exit"
        ]

    def display_menu(self):
        """Display the main menu with current selection highlighted"""
        self.console.clear()

        # Create a large, prominent header for "TaskFlow Studio" with red accent
        from rich.text import Text

        # Create the main header with red prominence
        header_text = Text(justify="center")
        header_text.append("╔════════════════════════════════════════════════════════════════════╗\n", style="bold bright_red")
        header_text.append("║                           ", style="bold bright_red")
        header_text.append("🚀 ", style="bold bright_red")
        header_text.append("T", style="bold bright_red")
        header_text.append("A", style="bold bright_yellow")
        header_text.append("S", style="bold bright_green")
        header_text.append("K", style="bold bright_cyan")
        header_text.append("F", style="bold bright_blue")
        header_text.append("L", style="bold bright_magenta")
        header_text.append("O", style="bold bright_white")
        header_text.append("W", style="bold bright_red")
        header_text.append(" ", style="bold bright_red")
        header_text.append("S", style="bold bright_yellow")
        header_text.append("T", style="bold bright_green")
        header_text.append("U", style="bold bright_cyan")
        header_text.append("D", style="bold bright_blue")
        header_text.append("I", style="bold bright_magenta")
        header_text.append("O", style="bold bright_white")
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
        total_tasks = len(self.task_manager.get_all_tasks())
        completed_tasks = len([task for task in self.task_manager.get_all_tasks() if task.completed])
        pending_tasks = total_tasks - completed_tasks

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

        self.console.print(stats_text)
        self.console.print(progress_text_obj)
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

        header_text = Text("📋 TASKFLOW STUDIO - TASK LIST 📋", style="bold bright_cyan on black")
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
        table.add_column("Title", style="white", width=25)
        table.add_column("Description", style="white", width=25)
        table.add_column("Status", style="white", width=12)
        table.add_column("Date Added", style="white", width=12)

        # Add row numbers for easy selection
        for idx, task in enumerate(sorted_tasks, 1):
            status_style = "bold bright_green" if task.completed else "bold bright_red"
            status_text = "Complete" if task.completed else "Pending"
            table.add_row(
                str(idx),  # Row number
                str(task.id),
                task.title,
                task.description or "",
                f"[{status_style}]{status_text}[/{status_style}]",
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

        if self.task_manager.add_task(title, description if description else None):
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

        if self.task_manager.update_task(task_id, new_title, new_description):
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

        try:
            # Try to convert to integer for ID search
            search_id = int(search_term)
            tasks = [task for task in self.task_manager.get_all_tasks() if task.id == search_id]
        except ValueError:
            # Search by title and description
            search_term_lower = search_term.lower()
            tasks = [task for task in self.task_manager.get_all_tasks()
                    if search_term_lower in task.title.lower() or
                    (task.description and search_term_lower in task.description.lower())]

        if tasks:
            self.console.print(f"[bold bright_green]Found {len(tasks)} matching task(s):[/bold bright_green]")
            self.console.print()

            table = Table(title="Search Results", show_header=True, header_style="bold bright_magenta")
            table.add_column("ID", style="bold bright_green", width=5)
            table.add_column("Title", style="white", width=25)
            table.add_column("Description", style="white", width=25)
            table.add_column("Status", style="white", width=12)
            table.add_column("Date Added", style="white", width=12)

            for task in tasks:
                status_style = "bold bright_green" if task.completed else "bold bright_red"
                status_text = "Complete" if task.completed else "Pending"
                table.add_row(
                    str(task.id),
                    task.title,
                    task.description or "",
                    f"[{status_style}]{status_text}[/{status_style}]",
                    task.created_at.strftime('%Y-%m-%d') if task.created_at else ''
                )

            self.console.print(table)
        else:
            self.console.print("[bold bright_yellow]No tasks found matching your search.[/bold bright_yellow]")

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
                    self.console.print("\n[bold bright_cyan]👋 Goodbye! Thanks for using TaskFlow Studio! 👋[/bold bright_cyan]")
                    break

                # Handle navigation and selection
                if choice == 'q':
                    self.console.print("\n[bold bright_cyan]👋 Goodbye! Thanks for using TaskFlow Studio! 👋[/bold bright_cyan]")
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
                    elif selected_option == "Export Tasks":
                        self.export_tasks_flow()
                    elif selected_option == "Import Tasks":
                        self.import_tasks_flow()
                    elif selected_option == "Search Tasks":
                        self.search_tasks_flow()
                    elif selected_option == "Task Statistics":
                        self.task_statistics_flow()
                    elif selected_option == "Exit":
                        self.console.print("\n[bold bright_cyan]👋 Goodbye! Thanks for using TaskFlow Studio! 👋[/bold bright_cyan]")
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
                        elif selected_option == "Export Tasks":
                            self.export_tasks_flow()
                        elif selected_option == "Import Tasks":
                            self.import_tasks_flow()
                        elif selected_option == "Search Tasks":
                            self.search_tasks_flow()
                        elif selected_option == "Task Statistics":
                            self.task_statistics_flow()
                        elif selected_option == "Exit":
                            self.console.print("\n[bold bright_cyan]👋 Goodbye! Thanks for using TaskFlow Studio! 👋[/bold bright_cyan]")
                            break
        except KeyboardInterrupt:
            self.console.print("\n\n[bold bright_cyan]👋 Goodbye! Thanks for using TaskFlow Studio! 👋[/bold bright_cyan]")


def main():
    app = MainMenuApp()
    app.run()


if __name__ == "__main__":
    main()