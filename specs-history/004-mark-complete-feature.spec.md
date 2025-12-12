# Spec: Mark Complete/Incomplete Feature

## Title
Mark Complete/Incomplete Feature Implementation

## Purpose
Implement the functionality to toggle the completion status of tasks in the in-memory todo list. This feature enables users to mark tasks as complete or incomplete by their unique identifiers.

## Inputs
- Task ID (integer, required)
- Command type (complete or incomplete - determined by the command used)

## Expected Behavior
1. System validates that the task ID exists in the in-memory task list
2. If the task exists, system toggles the completion status
3. If the task doesn't exist, system returns an error message
4. System returns confirmation of successful status change or error message
5. The task maintains all other properties except the completion status

## Acceptance Criteria
- [ ] System validates that task ID exists before attempting to change status
- [ ] System toggles the completion status of the task
- [ ] System supports both 'complete' and 'incomplete' commands
- [ ] System returns appropriate confirmation or error message
- [ ] Mark complete/incomplete operation is accessible via CLI commands
- [ ] Error handling for invalid or non-existent task IDs
- [ ] Confirmation message displayed after successful status change
- [ ] Updated status is reflected in task listings
- [ ] Unit tests cover positive and negative scenarios

## Technical Requirements
- Toggle task status functionality must be implemented in src/todo.py
- CLI interface must be updated in src/main.py if not already implemented
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
- Bulk status change operations