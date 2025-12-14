#!/usr/bin/env python3
"""
Professional CLI Task Manager with Arrow Key Navigation
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
    description: str
    status: str  # "Pending" or "Complete"
    date_added: str


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
                    self.tasks = [Task(**task) for task in data.get('tasks', [])]
                    self.next_id = data.get('next_id', 1)
            except (json.JSONDecodeError, KeyError):
                # If file is corrupted, start fresh
                self.tasks = []
                self.next_id = 1
        else:
            self.tasks = []
            self.next_id = 1

    def save_tasks(self):
        """Save tasks to JSON file"""
        data = {
            'tasks': [asdict(task) for task in self.tasks],
            'next_id': self.next_id
        }
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def add_task(self, description: str) -> bool:
        """Add a new task"""
        if not description.strip():
            return False

        task = Task(
            id=self.next_id,
            description=description.strip(),
            status="Pending",
            date_added=datetime.now().strftime("%Y-%m-%d")
        )
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return True

    def update_task(self, task_id: int, new_description: str) -> bool:
        """Update a task's description"""
        for task in self.tasks:
            if task.id == task_id:
                task.description = new_description.strip()
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

    def mark_complete(self, task_id: int) -> bool:
        """Mark a task as complete"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = "Complete"
                self.save_tasks()
                return True
        return False

    def mark_incomplete(self, task_id: int) -> bool:
        """Mark a task as incomplete"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = "Pending"
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


class TaskManagerApp:
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
            "Advanced Tasks"
        ]

    def display_menu(self):
        """Display the main menu with current selection highlighted"""
        self.console.clear()

        # Display centered, colorful header
        header_text = Text("🚀 CONSOLE APP 🚀", style="bold bright_cyan on black")
        header = Panel(header_text, expand=False, border_style="bright_cyan", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        # Display menu options with selection highlighting
        for i, option in enumerate(self.menu_options):
            if i == self.current_selection:
                self.console.print(f"[bold white on blue] > {option} [/bold white on blue]")
            else:
                self.console.print(f"   {option}")

        self.console.print()
        self.console.print("[bold bright_yellow]Use 'up'/'down' to navigate, Enter to select, 'q' to quit, or enter option number[/bold bright_yellow]")

    def display_task_list(self):
        """Display all tasks in a table format"""
        self.console.clear()

        header_text = Text("📋 CONSOLE APP - TASK LIST 📋", style="bold bright_cyan on black")
        header = Panel(header_text, expand=False, border_style="bright_cyan", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        tasks = self.task_manager.get_all_tasks()

        if not tasks:
            self.console.print("[bold bright_yellow]No tasks available.[/bold bright_yellow]")
            input("\nPress Enter to return to main menu...")
            return

        table = Table(title="All Tasks", show_header=True, header_style="bold bright_magenta")
        table.add_column("ID", style="bold bright_green", width=5)
        table.add_column("Description", style="white", width=40)
        table.add_column("Status", style="white", width=12)
        table.add_column("Date Added", style="white", width=12)

        for task in tasks:
            status_style = "bold bright_green" if task.status == "Complete" else "bold bright_red"
            table.add_row(
                str(task.id),
                task.description,
                f"[{status_style}]{task.status}[/{status_style}]",
                task.date_added
            )

        self.console.print(table)
        input("\nPress Enter to return to main menu...")

    def add_task_flow(self):
        """Handle the add task flow"""
        self.console.clear()

        header_text = Text("ADD NEW TASK", style="bold bright_cyan")
        header = Panel(header_text, expand=False, border_style="bright_cyan", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        description = Prompt.ask("[bold bright_white]Enter task description[/bold bright_white]")

        if self.task_manager.add_task(description):
            self.console.print("\n[bold bright_green]✓ Task added successfully![/bold bright_green]")
        else:
            self.console.print("\n[bold bright_red]✗ Error: Task description cannot be empty.[/bold bright_red]")

        input("\nPress Enter to return to main menu...")

    def update_task_flow(self):
        """Handle the update task flow"""
        self.console.clear()

        header_text = Text("UPDATE TASK", style="bold bright_cyan")
        header = Panel(header_text, expand=False, border_style="bright_cyan", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        try:
            task_id = int(Prompt.ask("[bold bright_white]Enter Task ID to update[/bold bright_white]"))
        except ValueError:
            self.console.print("\n[bold bright_red]✗ Error: Invalid Task ID.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            self.console.print(f"\n[bold bright_red]✗ Error: Task with ID {task_id} not found.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        new_description = Prompt.ask(f"[bold bright_white]Enter new description (current: {task.description})[/bold bright_white]", default=task.description)

        if self.task_manager.update_task(task_id, new_description):
            self.console.print(f"\n[bold bright_green]✓ Task {task_id} updated successfully![/bold bright_green]")
        else:
            self.console.print(f"\n[bold bright_red]✗ Error: Failed to update task {task_id}.[/bold bright_red]")

        input("\nPress Enter to return to main menu...")

    def delete_task_flow(self):
        """Handle the delete task flow"""
        self.console.clear()

        header_text = Text("DELETE TASK", style="bold bright_cyan")
        header = Panel(header_text, expand=False, border_style="bright_cyan", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        try:
            task_id = int(Prompt.ask("[bold bright_white]Enter Task ID to delete[/bold bright_white]"))
        except ValueError:
            self.console.print("\n[bold bright_red]✗ Error: Invalid Task ID.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            self.console.print(f"\n[bold bright_red]✗ Error: Task with ID {task_id} not found.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        confirm = Prompt.ask(f"[bold bright_white]Are you sure you want to delete task '{task.description}'? (y/n)[/bold bright_white]", default="n")

        if confirm.lower() in ['y', 'yes']:
            if self.task_manager.delete_task(task_id):
                self.console.print(f"\n[bold bright_green]✓ Task {task_id} deleted successfully![/bold bright_green]")
            else:
                self.console.print(f"\n[bold bright_red]✗ Error: Failed to delete task {task_id}.[/bold bright_red]")
        else:
            self.console.print("\n[bold bright_yellow]ℹ Deletion cancelled.[/bold bright_yellow]")

        input("\nPress Enter to return to main menu...")

    def mark_complete_flow(self):
        """Handle the mark as complete flow"""
        self.console.clear()

        header_text = Text("MARK TASK COMPLETE", style="bold bright_cyan")
        header = Panel(header_text, expand=False, border_style="bright_cyan", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        try:
            task_id = int(Prompt.ask("[bold bright_white]Enter Task ID to mark as complete[/bold bright_white]"))
        except ValueError:
            self.console.print("\n[bold bright_red]✗ Error: Invalid Task ID.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            self.console.print(f"\n[bold bright_red]✗ Error: Task with ID {task_id} not found.[/bold bright_red]")
            input("\nPress Enter to return to main menu...")
            return

        if self.task_manager.mark_complete(task_id):
            self.console.print(f"\n[bold bright_green]✓ Task {task_id} marked as complete![/bold bright_green]")
        else:
            self.console.print(f"\n[bold bright_red]✗ Error: Failed to mark task {task_id} as complete.[/bold bright_red]")

        input("\nPress Enter to return to main menu...")

    def advanced_tasks_menu(self):
        """Display advanced tasks menu"""
        self.console.clear()

        header_text = Text("ADVANCED TASKS", style="bold bright_cyan")
        header = Panel(header_text, expand=False, border_style="bright_cyan", padding=(1, 2))
        self.console.print()
        self.console.print(header, justify="center")
        self.console.print()

        advanced_options = [
            "Export Tasks",
            "Import Tasks",
            "Filter Tasks",
            "Search Tasks",
            "Statistics"
        ]

        for option in advanced_options:
            self.console.print(f"  {option}")

        self.console.print("\n[bold bright_yellow]This feature is under development.[/bold bright_yellow]")
        input("\nPress Enter to return to main menu...")

    def run(self):
        """Main application loop with simple input navigation"""
        try:
            while True:
                self.display_menu()

                # Get user input
                try:
                    choice = input("\n[bold bright_cyan]Select option: [/bold bright_cyan]").strip().lower()
                except EOFError:
                    self.console.print("\n[bold bright_cyan]Goodbye![/bold bright_cyan]")
                    break

                # Handle navigation and selection
                if choice == 'q':
                    self.console.print("\n[bold bright_cyan]Goodbye![/bold bright_cyan]")
                    break
                elif choice == 'up' or choice == 'u':
                    self.current_selection = (self.current_selection - 1) % len(self.menu_options)
                elif choice == 'down' or choice == 'd':
                    self.current_selection = (self.current_selection + 1) % len(self.menu_options)
                elif choice == '' or choice == 'enter' or choice == 'e':
                    # Execute the selected option
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
                    elif selected_option == "Advanced Tasks":
                        self.advanced_tasks_menu()
                elif choice.isdigit():
                    # Allow direct selection by number
                    option_index = int(choice) - 1
                    if 0 <= option_index < len(self.menu_options):
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
                        elif selected_option == "Advanced Tasks":
                            self.advanced_tasks_menu()
        except KeyboardInterrupt:
            self.console.print("\n\n[bold bright_cyan]Goodbye![/bold bright_cyan]")


def main():
    app = TaskManagerApp()
    app.run()


if __name__ == "__main__":
    main()