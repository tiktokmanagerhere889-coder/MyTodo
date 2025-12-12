'''
Main entry point for the Todo application
Provides the command-line interface for interacting with tasks
'''

import sys
from typing import Optional
from .todo import TodoManager


def print_help():
    """Prints the help message with available commands"""
    print("Todo App - Command Line Interface")
    print("Usage: python main.py [command] [arguments]")
    print()
    print("Commands:")
    print("  add <title> [description]     - Add a new task")
    print("  list                          - List all tasks")
    print("  update <id> [title] [desc]    - Update a task")
    print("  delete <id>                   - Delete a task")
    print("  complete <id>                 - Mark task as complete")
    print("  incomplete <id>               - Mark task as incomplete")
    print("  task-manager                  - Launch advanced task manager")
    print("  menu                          - Launch main menu interface")
    print("  help                          - Show this help message")


def main():
    """Main function to handle command line arguments and execute commands"""
    todo_manager = TodoManager()

    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "help":
        print_help()
    elif command == "add":
        if len(sys.argv) < 3:
            print("Error: Title is required for adding a task")
            print("Usage: python main.py add <title> [description]")
            return

        title = sys.argv[2]
        description = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else None

        new_task = todo_manager.add_task(title, description)
        print(f"Task added successfully!")
        print(f"ID: {new_task.id}")
        print(f"Title: {new_task.title}")
        if new_task.description:
            print(f"Description: {new_task.description}")
        print(f"Status: {'Completed' if new_task.completed else 'Incomplete'}")
    elif command == "list":
        tasks = todo_manager.get_all_tasks()
        if not tasks:
            print("No tasks found.")
        else:
            print(f"Total tasks: {len(tasks)}")
            for task in tasks:
                status = "✓" if task.completed else "○"
                print(f"[{status}] {task.id}: {task.title}")
                if task.description:
                    print(f"    Description: {task.description}")
                print()
    elif command == "update":
        if len(sys.argv) < 3:
            print("Error: Task ID is required for updating a task")
            print("Usage: python main.py update <id> [title] [description]")
            return

        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print("Error: Task ID must be a number")
            return

        title = None
        description = None

        if len(sys.argv) >= 4:
            title = sys.argv[3] if sys.argv[3] != "None" else None
        if len(sys.argv) >= 5:
            description = " ".join(sys.argv[4:])

        if todo_manager.update_task(task_id, title, description):
            print(f"Task {task_id} updated successfully!")
        else:
            print(f"Task with ID {task_id} not found.")
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: Task ID is required for deleting a task")
            print("Usage: python main.py delete <id>")
            return

        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print("Error: Task ID must be a number")
            return

        if todo_manager.delete_task(task_id):
            print(f"Task {task_id} deleted successfully!")
        else:
            print(f"Task with ID {task_id} not found.")
    elif command in ["complete", "incomplete"]:
        if len(sys.argv) < 3:
            print(f"Error: Task ID is required for marking a task as {command}")
            print(f"Usage: python main.py {command} <id>")
            return

        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print("Error: Task ID must be a number")
            return

        # Check if task exists before toggling
        task = todo_manager.get_task_by_id(task_id)
        if task is None:
            print(f"Task with ID {task_id} not found.")
            return

        if command == "complete":
            if todo_manager.toggle_task_status(task_id):
                print(f"Task {task_id} marked as complete!")
            else:
                print(f"Task with ID {task_id} not found.")
        elif command == "incomplete":
            if todo_manager.toggle_task_status(task_id):
                print(f"Task {task_id} marked as incomplete!")
            else:
                print(f"Task with ID {task_id} not found.")
    elif command == "task-manager":
        from .task_manager import main as task_manager_main
        task_manager_main()
    elif command == "menu":
        from .main_menu import main as main_menu_main
        main_menu_main()
    else:
        print(f"Unknown command: {command}")
        print()
        print_help()


if __name__ == "__main__":
    main()