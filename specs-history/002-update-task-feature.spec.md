# Spec: Update Task Feature

## Title
Update Task Feature Implementation

## Purpose
Implement the functionality to update existing tasks in the in-memory todo list. This feature enables users to modify the title and description of tasks by their unique identifiers.

## Inputs
- Task ID (integer, required)
- New task title (string, optional)
- New task description (string, optional)

## Expected Behavior
1. System validates that the task ID exists in the in-memory task list
2. If the task exists, system updates the specified fields (title and/or description)
3. If the task doesn't exist, system returns an error message
4. System returns confirmation of successful update or error message
5. Updated task maintains the same ID and other unchanged properties

## Acceptance Criteria
- [ ] System validates that task ID exists before attempting update
- [ ] System updates only the fields that are provided (partial updates allowed)
- [ ] System preserves unchanged properties (ID, completion status, creation timestamp)
- [ ] Update task operation is accessible via CLI command
- [ ] Error handling for invalid or non-existent task IDs
- [ ] Confirmation message displayed after successful task update
- [ ] Updated task can be retrieved via View Tasks feature
- [ ] Unit tests cover positive and negative scenarios

## Technical Requirements
- Update task functionality must be implemented in src/todo.py
- CLI interface must be updated in src/main.py
- Follow clean code practices with proper error handling
- Maintain separation of concerns between models, business logic, and CLI

## Dependencies
- Task model definition
- In-memory storage mechanism
- CLI framework for user interaction
- Existing Add Task functionality

## Out of Scope
- Database persistence (in-memory only as per constitution)
- Advanced validation beyond basic input validation
- Bulk update operations