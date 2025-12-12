<!--
Sync Impact Report:
- Version change: 0.1.0 → 1.0.0
- Modified principles: All principles replaced with project-specific content
- Added sections: Specification Rules, Technical Stack Requirements, Code Quality Rules, Agent Behavior Rules
- Removed sections: None
- Templates requiring updates: ✅ All templates updated to match new constitution
- Follow-up TODOs: None
-->
# Todo In-Memory Python Console Application Constitution

## Core Principles

### I. Spec-Driven Development
All development must follow spec-driven engineering using Spec-Kit Plus. Every feature, change request, or enhancement must be documented as a spec file inside specs-history/ before any code implementation. Code generation must be performed by Claude Code based strictly on spec files. No code may be generated without an associated spec.

### II. In-Memory Storage Constraint
The system must implement a command-line Todo application in Python with all tasks stored in memory only. No database or external storage is permitted. This constraint ensures simplicity and aligns with Phase I requirements for a lightweight console application.

### III. Five Core Features Only (NON-NEGOTIABLE)
Only the five mandatory core features are implemented in Phase I: Add Task, View Tasks, Update Task, Delete Task, and Mark Complete/Incomplete. No additional features or functionality may be implemented without explicit specification and approval. This ensures focus on core requirements.

### IV. Python 3.13+ and UV Dependency Management
The system must run on Python 3.13+ with UV as the package/dependency tool. All development operations must use Claude Code and Spec-Kit Plus. This ensures consistent and modern development environment across all project operations.

### V. Clean Code Architecture
Code must follow clean code practices with modular design separated by responsibility. The codebase must follow a clean Python structure with src/main.py, src/todo.py, and src/models/task.py. Functions and classes must include clear names reflecting their purpose. All logic must be modular and separated by responsibility.

### VI. Version Control with Spec Integration
Every spec and code change must be committed individually with commit messages that clearly reference the related spec file. No code changes are allowed without a matching spec. This ensures traceability and maintains the spec-driven development workflow.

## Specification Rules
Each new spec must have a unique incremental filename inside specs-history/. Each spec must include Title, Purpose, Inputs, Expected behavior, and Acceptance criteria. Claude must generate or modify code only after reading the spec. This ensures all development is properly documented and traceable.

## Technical Stack Requirements
The system must run on Python 3.13+ and UV (Package/dependency tool). Development operations must use Claude Code and Spec-Kit Plus. The repository must contain constitution.md, README.md, and CLAUDE.md at the root level. The repository must include specs-history/ for specification files and src/ for all Python source code.

## Code Quality Rules
Code must follow clean code practices. All logic must be modular and separated by responsibility. No hard-coded paths or credentials are permitted. Functions and classes must include clear names reflecting their purpose. This ensures maintainable and secure code.

## Agent Behavior Rules
Claude must obey this constitution for all code generation. Claude must not hallucinate, assume, or invent unspecified behavior. If a request violates this constitution, Claude must refuse and reference the specific violated rule. All responses from Claude Code must be deterministic and spec-driven.

## Governance
This constitution governs all development operations of Phase I. All agents must consistently read and follow this constitution before executing any instruction. Violations must result in an explicit refusal with the violated rule number. Amendments require explicit user consent and documentation of changes. All development must comply with this constitution for every operation, generation, or modification.

**Version**: 1.0.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-09
