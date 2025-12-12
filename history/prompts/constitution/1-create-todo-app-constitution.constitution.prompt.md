---
id: 1
title: Create Todo App Constitution
stage: constitution
date: 2025-12-09
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: hassan
command: /sp.constitution
labels: ["constitution","todo-app","spec-driven"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
This constitution defines the rules, workflow, and responsibilities for all AI agents and tools used in building the Phase I Todo In-Memory Python Console Application. All agents must comply with this constitution for every operation, generation, or modification.

1. Project Scope

1.1 The system must implement a command-line Todo application in Python.
1.2 All tasks are stored in memory only; no database or external storage is used.
1.3 Only the five mandatory core features are implemented in Phase I:

Add Task

View Tasks

Update Task

Delete Task

Mark Complete / Incomplete

2. Development Methodology

2.1 Development must follow spec-driven engineering using Spec-Kit Plus.
2.2 Every feature, change request, or enhancement must be documented as a spec file inside specs-history/.
2.3 Code generation must be performed by Claude Code based strictly on spec files.
2.4 Manual boilerplate coding is not permitted; Claude must produce all boilerplate.

3. Repository Structure Requirements

3.1 The repository must contain the following root-level files:

constitution.md

README.md

CLAUDE.md

3.2 The repository must include the following folders:

specs-history/ for specification files

src/ for all Python source code

3.3 The codebase must follow a clean Python structure similar to:

src/
  main.py
  todo.py
  models/
    task.py


3.4 Each file's purpose must be clearly defined in its respective spec.

4. Technical Stack Requirements

4.1 The system must run on:

Python 3.13+

UV (Package/dependency tool)

4.2 Development operations must use:

Claude Code

Spec-Kit Plus

5. Functional Requirements

5.1 Add Task

Generates unique task ID

Accepts title and description

5.2 View Tasks

Lists all tasks

Shows completion status

5.3 Update Task

Allows modification of title and description

5.4 Delete Task

Deletes by task ID

5.5 Mark Complete / Incomplete

Toggles status using task ID

6. Specification Rules

6.1 Each new spec must have a unique incremental filename inside specs-history/.
6.2 Each spec must include:

Title

Purpose

Inputs

Expected behavior

Acceptance criteria

6.3 Claude must generate or modify code only after reading the spec.
6.4 No code may be generated without an associated spec.

7. Code Quality Rules

7.1 Code must follow clean code practices.
7.2 All logic must be modular and separated by responsibility.
7.3 No hard-coded paths or credentials are permitted.
7.4 Functions and classes must include clear names reflecting their purpose.

8. Agent Behavior Rules

8.1 Claude must obey this constitution for all code generation.
8.2 Claude must not hallucinate, assume, or invent unspecified behavior.
8.3 If a request violates this constitution, Claude must refuse and reference the specific violated rule.
8.4 All responses from Claude Code must be deterministic and spec-driven.

9. Deliverables

9.1 A fully functional CLI Todo app.
9.2 All spec files in specs-history/.
9.3 All Python code in src/.
9.4 Professional README.md with installation, execution, and usage instructions.
9.5 CLAUDE.md describing how to work with Claude Code and spec-driven workflows.

10. Version Control Rules

10.1 Every spec and code change must be committed individually.
10.2 Commit messages must clearly reference the related spec file.
10.3 No code changes are allowed without a matching spec.

11. Constitution Enforcement

11.1 This constitution governs all development operations of Phase I.
11.2 All agents must consistently read and follow this constitution before executing any instruction.
11.3 Violations must result in an explicit refusal with the violated rule number.
```

## Response snapshot

Updated the constitution file at `.specify/memory/constitution.md` to reflect the specific requirements for the Todo In-Memory Python Console Application. The new constitution includes:

- Core Principles: Spec-Driven Development, In-Memory Storage Constraint, Five Core Features Only, Python 3.13+ and UV Dependency Management, Clean Code Architecture, and Version Control with Spec Integration
- Specification Rules: Requirements for spec files and incremental naming
- Technical Stack Requirements: Python 3.13+, UV, Claude Code, and Spec-Kit Plus
- Code Quality Rules: Clean code practices and modular design
- Agent Behavior Rules: Compliance with constitution and deterministic responses
- Governance: Amendment procedures and compliance requirements

## Outcome

- ✅ Impact: Created foundational constitution document that governs all development operations
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md with project-specific constitution
- 🔁 Next prompts: Proceed with creating spec files for individual features
- 🧠 Reflection: Constitution now serves as authoritative guide for all development activities

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS - Constitution follows required structure and incorporates all specified requirements
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Begin creating spec files based on constitution requirements