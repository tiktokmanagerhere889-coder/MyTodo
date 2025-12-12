#!/usr/bin/env python3
"""
Feature Summary Script for Todo CLI Application
Displays a polished summary of all Phase I features with rich formatting.
"""

from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text


def main():
    # Define custom theme
    todo_theme = Theme({
        "header": "bold bright_cyan",
        "feature_title": "bold bright_magenta",
        "description": "bright_white",
        "valid": "bright_green",
        "warning": "bright_yellow",
        "error": "bold bright_red"
    })

    # Create console with custom theme
    console = Console(theme=todo_theme)

    # Print top-level heading
    console.print("\nTodo CLI — Phase I Feature Summary\n", style="header", justify="center")

    # Define features with icons and descriptions
    features = [
        {
            "icon": "✏️",
            "name": "Add Task",
            "description": "Creates new tasks with unique IDs, titles, and descriptions"
        },
        {
            "icon": "📋",
            "name": "View Tasks",
            "description": "Lists all tasks with completion status and details"
        },
        {
            "icon": "✏️",
            "name": "Update Task",
            "description": "Modifies existing task titles and descriptions by ID"
        },
        {
            "icon": "🗑️",
            "name": "Delete Task",
            "description": "Removes tasks from the in-memory list by ID"
        },
        {
            "icon": "✅ / ❌",
            "name": "Mark Complete/Incomplete",
            "description": "Toggles task completion status (complete/incomplete)"
        }
    ]

    # Render each feature as a panel
    for feature in features:
        feature_text = Text.assemble(
            (f"{feature['icon']} ", "feature_title"),
            (feature['name'], "feature_title"),
            "\n",
            (feature['description'], "description")
        )
        panel = Panel(feature_text, expand=True)
        console.print(panel)
        console.print()  # Add spacing between panels

    # Print usage reminder in dim style
    console.print("Run [italic]python -m src.main help[/italic] to see full list of commands.", style="dim")


if __name__ == "__main__":
    main()