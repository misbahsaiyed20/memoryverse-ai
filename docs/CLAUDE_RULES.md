# Claude Implementation Rules

## Purpose

This document defines the implementation rules for MemoryVerse AI.

Every implementation AI (Claude, Gemini, Copilot, etc.) MUST follow these rules before writing any code.

The goal is to maintain a consistent architecture throughout the project and prevent unnecessary redesigns.

---

# Rule 1 — Understand Before Coding

Before writing any code:

1. Read PROJECT_CONTEXT.md.
2. Read PROJECT_STATUS.md.
3. Inspect the existing codebase.
4. Identify where the new feature belongs.
5. Explain the implementation plan.
6. Only then begin coding.

Never write code without understanding the current architecture.

---

# Rule 2 — Never Redesign

Do NOT redesign the project.

Do NOT introduce a new architecture.

Do NOT move files unless explicitly requested.

Do NOT rename services.

Do NOT replace working implementations.

Extend the existing architecture instead.

---

# Rule 3 — Follow Existing Patterns

Always reuse existing project patterns.

Examples:

- StorageService / LocalStorageService
- EmbeddingProvider abstraction
- Dependency Injection
- SQLAlchemy Session pattern
- FastAPI routers
- Service layer

New code should look like it belongs to the existing project.

---

# Rule 4 — Single Responsibility

Each class should have one responsibility.

Routes

Responsible for:

- Request validation
- Authentication
- Calling services
- Returning responses

Services

Responsible for:

- Business logic
- Orchestration

Infrastructure

Responsible for:

- External systems
- Firebase
- Gemini
- ChromaDB
- Local Storage

---

# Rule 5 — Never Put Business Logic Inside Routes

Routes should remain thin.

Incorrect:

Route

↓

Gemini

↓

Database

Correct:

Route

↓

Service

↓

Infrastructure

---

# Rule 6 — Database Is Source of Truth

PostgreSQL is always the source of truth.

Never store permanent business data inside:

- ChromaDB
- Gemini
- Firebase

---

# Rule 7 — ChromaDB Rules

ChromaDB stores only:

- Embeddings
- Chunk metadata

Never store:

- Users
- Skills
- Projects
- Knowledge graph
- Business entities

---

# Rule 8 — Gemini Rules

Gemini is used only for:

- Knowledge extraction
- Embeddings
- Future reasoning

Gemini is never the permanent storage.

---

# Rule 9 — Dependency Injection

Prefer constructor injection.

Avoid global mutable state.

Reuse existing dependency patterns.

---

# Rule 10 — Configuration

Never hardcode:

- API Keys
- Secrets
- File paths
- Database URLs

Use environment variables.

---

# Rule 11 — Error Handling

Catch expected errors.

Log useful messages.

Never silently ignore failures.

If a non-critical component fails (for example embeddings), the remaining pipeline should continue whenever possible.

---

# Rule 12 — Logging

Log:

- Important operations
- Warnings
- Recoverable failures

Avoid excessive logging.

Never log secrets.

---

# Rule 13 — Backward Compatibility

Do not break existing APIs.

Do not remove existing functionality.

Prefer additive changes.

---

# Rule 14 — Database Changes

Do NOT modify the schema unless absolutely necessary.

If a migration is required:

Explain:

- Why
- Impact
- Rollback strategy

---

# Rule 15 — Frontend

Do not redesign the UI.

Reuse existing components.

Follow the current design language.

---

# Rule 16 — Documentation

Every implementation must explain:

## Files Created

Example

backend/app/services/example_service.py

---

## Files Modified

List every modified file.

---

## Why

Explain every architectural decision.

---

## Testing

Explain exactly how the feature was tested.

---

## Confirmation

Confirm that:

- Existing functionality still works.
- No unrelated files were modified.
- Architecture remains consistent.

---

# Rule 17 — Testing Requirements

Every implementation should verify:

- Happy path
- Invalid input
- Error handling
- Existing functionality
- Backward compatibility

---

# Rule 18 — Never Guess

If project behavior is unclear:

Inspect the existing code.

Do not invent architecture.

Do not assume file locations.

---

# Rule 19 — Sprint Boundaries

Only implement what belongs to the requested sprint.

Do not implement future features early.

Do not skip planned architecture.

---

# Rule 20 — Clean Code

Follow:

- SOLID principles
- DRY
- Meaningful names
- Type hints
- Small functions
- Readable code

---

# Required Response Format

Every implementation response must contain:

## Files Created

## Files Modified

## Architecture Decisions

## Testing Performed

## Confirmation

Nothing should be omitted.

---

# Things Never To Change

Without explicit approval, never:

- Replace FastAPI
- Replace PostgreSQL
- Replace ChromaDB
- Replace Firebase
- Replace Gemini
- Rename folders
- Rename services
- Change project architecture
- Remove abstractions
- Rewrite completed sprints

---

# Definition of Done

A task is complete only if:

- Code compiles.
- Existing functionality remains intact.
- Tests pass.
- Documentation is updated if required.
- Architecture remains consistent.
- No unnecessary changes were introduced.

---

# AI Handoff

Whenever continuing this project:

1. Read PROJECT_CONTEXT.md.
2. Read PROJECT_STATUS.md.
3. Read CLAUDE_RULES.md.
4. Inspect the current project.
5. Summarize your understanding.
6. Explain the implementation plan.
7. Implement only the requested sprint.
8. Test thoroughly.
9. Provide implementation summary.

Following these rules ensures consistent development across multiple AI sessions and contributors.