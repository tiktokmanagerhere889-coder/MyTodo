# TaskFlow Studio - Professional CLI Task Manager

A feature-rich, professional command-line task management application with a beautiful, interactive interface.

## 🚀 Features

- **Add Tasks**: Create new tasks with titles and descriptions
- **View Tasks**: Display all tasks with completion status and statistics
- **Update Tasks**: Modify existing task titles and descriptions
- **Delete Tasks**: Remove tasks with confirmation
- **Mark Complete/Incomplete**: Toggle task completion status
- **Advanced Features**: Export/import tasks, search functionality, statistics dashboard
- **Beautiful UI**: Colorful interface with 3D headers, progress bars, and professional styling
- **Persistent Storage**: Tasks saved to JSON file automatically

## 🛠️ Technologies Used

- Python 3
- Rich library for colorful terminal interfaces
- Dataclasses for task management

## 📋 Requirements

- Python 3.7+
- Rich library (`pip install rich`)

## 🚀 Installation & Usage

### Clone the repository:
```bash
git clone https://github.com/tiktokmanagerhere889-coder/MyTodo.git
cd MyTodo
```

### Install dependencies:
```bash
pip install rich
```

### Run the application:

#### Main CLI Interface:
```bash
# Add a task
python -m src.main add "Task Title" "Task Description"

# List all tasks
python -m src.main list

# Update a task
python -m src.main update 1 "New Title" "New Description"

# Delete a task
python -m src.main delete 1

# Mark task as complete
python -m src.main complete 1

# Mark task as incomplete
python -m src.main incomplete 1

# Show help
python -m src.main help
```

#### TaskFlow Studio (Professional Interface):
```bash
# Launch the professional task manager with colorful UI
python -m src.main menu
```

## 🎨 User Interface

The TaskFlow Studio features:
- Beautiful 3D-styled headers with color gradients
- Interactive menu with keyboard navigation (W/S keys or number selection)
- Real-time task statistics and progress visualization
- Color-coded status indicators
- Responsive design with rich formatting

## 📁 Project Structure

```
MyTodo/
├── src/                    # Source code
│   ├── main.py            # Main CLI application
│   ├── todo.py            # Core task management
│   ├── models/            # Data models
│   │   └── task.py        # Task dataclass
│   └── main_menu.py       # TaskFlow Studio interface
├── tasks.json             # Task storage file
├── README.md              # This file
├── CLAUDE.md              # Development documentation
└── .specify/              # Spec-driven development files
```

## 🎯 Core Functionality

1. **Add Task**: Create tasks with unique IDs, titles, and descriptions
2. **View Tasks**: List all tasks with completion status and statistics
3. **Update Task**: Modify existing task titles and descriptions
4. **Delete Task**: Remove tasks with confirmation
5. **Mark Complete/Incomplete**: Toggle task completion status

## 📊 Advanced Features

- **Export/Import**: Save and load tasks from external files
- **Search**: Find tasks by title or description
- **Statistics**: View completion rates and task analytics
- **Persistent Storage**: Automatic saving and loading of tasks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Rich library for beautiful terminal interfaces
- Python community for excellent development tools