
# 🚀 MEMORYVERSE AI — PROJECT MASTER CONTEXT (v2.0)

**Version:** 2.0
**Status:** Sprint 2 Completed → Sprint 3 Planning
**Purpose:** Permanent project reference for all future development.

---

# 1. Project Vision

MemoryVerse AI is an AI-powered **Digital Identity & Career Intelligence Platform**.

The goal is to transform fragmented academic and professional documents into an intelligent, searchable, evidence-backed **Career Brain** that helps users understand, organize, and interact with their professional identity.

This is **not** just another RAG chatbot.

The product is an intelligent career assistant that always provides trustworthy answers backed by document evidence.

---

# 2. Ultimate Goal

Build a hackathon-winning project that is:

* technically excellent
* visually impressive
* AI-driven
* trustworthy
* production-quality
* memorable during judging

Every development decision must increase the project's chances of winning.

---

# 3. Decision Authority

## ChatGPT is the Project Architect.

ChatGPT decides:

* overall architecture
* sprint planning
* database schema
* API contracts
* roadmap
* feature prioritization
* AI architecture
* scalability
* security
* implementation order
* code review
* project strategy

---

## Claude is the Senior Implementation Engineer.

Claude is responsible ONLY for implementation.

Claude may:

* write code
* improve implementation
* optimize performance
* ask implementation questions

Claude may NEVER:

* redesign architecture
* change sprint scope
* rename APIs
* change database design
* modify project vision
* introduce new frameworks without approval

Architecture is always finalized before Claude writes code.

---

# 4. Product Philosophy

MemoryVerse AI must be:

Evidence-first.

Database-first.

AI-assisted.

Never AI-dependent.

The system should never hallucinate.

Every answer must be explainable.

Every extracted fact must link back to its source document.

---

# 5. Core Principles

## PostgreSQL

The database is the **single source of truth**.

---

## Gemini

Gemini performs reasoning only.

Gemini never permanently stores knowledge.

---

## ChromaDB

Stores semantic embeddings only.

Never acts as the source of truth.

---

## Career Brain

Career Brain is the central knowledge model.

Every uploaded document enriches the Career Brain.

---

# 6. High-Level Architecture

```
User

↓

Authentication

↓

Upload

↓

Storage

↓

Metadata

↓

Text Extraction

↓

Chunking

↓

Gemini Structured Extraction

↓

Career Brain

↓

Evidence Links

↓

Embeddings (ChromaDB)

↓

Hybrid Retrieval

↓

Verse AI

↓

Dashboard

↓

Career Intelligence

↓

Timeline

↓

Analytics
```

---

# 7. Technology Stack

## Frontend

* Next.js 15
* TypeScript
* Tailwind CSS
* shadcn/ui

---

## Backend

* FastAPI
* SQLAlchemy
* Pydantic

---

## Authentication

Firebase Authentication

Google Login

Firebase Admin SDK

---

## Database

PostgreSQL

---

## Storage

StorageService abstraction

Local storage first

Cloud storage later

---

## AI

Gemini

ChromaDB

RAG

---

## Version Control

Git

GitHub

---

# 8. Coding Standards

Always follow:

* SOLID Principles
* DRY
* Clean Architecture
* Modular Design
* Type Safety
* Dependency Injection where appropriate
* Proper logging
* Proper validation
* Meaningful naming
* Small reusable functions
* Centralized configuration
* Production-quality code

No shortcuts.

---

# 9. Architecture Rules

Routes only call services.

Services contain business logic.

Database models remain isolated.

Configuration lives only in config.py.

Never duplicate logic.

Never hardcode secrets.

Everything should remain modular and scalable.

---

# 10. Security Rules

Never commit:

```
.env

.env.local

firebase-service-account.json

node_modules

.venv

__pycache__
```

Always:

* validate uploaded files
* verify Firebase tokens
* validate MIME types
* validate file size
* sanitize filenames
* secure API endpoints

---

# 11. Git Workflow

Every sprint ends with:

```
git status

git add .

git commit

git push
```

Never push secrets.

Every sprint should have one meaningful commit.

---

# 12. Development Workflow

Every sprint must follow this sequence.

```
Architecture Design

↓

Database Design

↓

API Design

↓

Folder Structure Review

↓

Security Review

↓

Implementation Plan

↓

Claude Prompt

↓

Claude Implementation

↓

ChatGPT Code Review

↓

Testing

↓

Git Commit

↓

GitHub Push
```

No implementation starts before architecture is approved.

---

# 13. Sprint Roadmap

## ✅ Sprint 1

Foundation

Completed.

Included:

* Next.js setup
* FastAPI setup
* PostgreSQL connection
* Storage abstraction
* Health API
* API versioning
* README

---

## ✅ Sprint 2

Authentication

Completed.

Included:

* Firebase Authentication
* Google Login
* Firebase Admin verification
* Protected routes
* User model
* Dashboard
* User creation
* PostgreSQL integration
* GitHub setup

Everything verified working.

---

## Sprint 3

Document Upload System

Includes:

* upload API
* document model
* metadata
* secure uploads
* storage implementation
* CRUD
* dashboard integration

No AI.

---

## Sprint 4

Document Processing

* PDF extraction
* DOCX extraction
* OCR preparation

---

## Sprint 5

Chunking Engine

* smart chunking
* overlap
* metadata

---

## Sprint 6

Gemini Structured Extraction

Extract:

* skills
* projects
* education
* experience
* certificates
* technologies
* organizations

Return structured JSON.

---

## Sprint 7

Career Brain

Knowledge Graph

Evidence Links

Entity Relationships

---

## Sprint 8

Embeddings

ChromaDB

Semantic Indexing

---

## Sprint 9

Hybrid Search

Keyword

Semantic

Evidence Ranking

---

## Sprint 10

Verse AI

Evidence-backed conversational AI.

---

## Sprint 11

Career Intelligence

Generate:

* missing skills
* strengths
* weaknesses
* resume insights
* career timeline
* learning progression
* certificate analytics
* project analytics

---

## Sprint 12

Polish

Performance

Deployment

Documentation

Presentation

Demo

---

# 14. Hackathon Winning Strategy

The project must excel in four areas.

## 1. Engineering

Clean architecture.

Scalable.

Professional code.

---

## 2. AI

Evidence-backed.

Reliable.

Explainable.

No hallucinations.

---

## 3. User Experience

Modern UI.

Fast.

Beautiful.

Interactive.

---

## 4. Demo

Every feature must strengthen the final demo.

If a feature doesn't improve the demo, reconsider building it.

---

# 15. Demo Philosophy

The demo should tell a story:

```
Login

↓

Upload Resume

↓

Upload Certificates

↓

Career Brain builds automatically

↓

Skills appear

↓

Projects appear

↓

Timeline appears

↓

Insights generated

↓

Judge asks:

"Where did this answer come from?"

↓

Click:

Show Evidence

↓

Original document opens

↓

Relevant text highlighted
```

This creates trust and showcases the system's intelligence.

---

# 16. Current Project Status

Current Sprint:

Sprint 2

Status:

Completed successfully.

Verified:

✅ PostgreSQL connected

✅ Firebase Authentication working

✅ Google Login working

✅ Backend healthy

✅ Dashboard working

✅ User creation stored in PostgreSQL

✅ GitHub configured

✅ Sprint 2 completed and pushed

Branch:

main

---

# 17. Definition of Done

A sprint is complete only if:

* backend builds
* frontend builds
* APIs tested
* database verified
* UI verified
* security reviewed
* GitHub updated
* documentation updated
* ChatGPT reviews implementation

---

# 18. Rules for Every Future Chat

When this document is provided:

Do NOT restart the project.

Do NOT redesign architecture.

Do NOT repeat previous work.

Continue from the current sprint.

Preserve all previous architectural decisions unless explicitly instructed otherwise.

---

# 19. Immediate Next Objective

Sprint 3.

Before writing any code:

1. Design Sprint 3 architecture.
2. Design database schema.
3. Design storage layer.
4. Design API contracts.
5. Design validation.
6. Review scalability.
7. Review security.
8. Generate a detailed Claude implementation prompt.
9. Review the implementation after Claude completes it.
10. Commit and push only after verification.

---

# 20. Success Criteria

The project succeeds if it delivers:

* A seamless document upload experience.
* An evidence-backed Career Brain.
* Trustworthy AI responses.
* Clear career insights.
* A polished, memorable demo.
* Clean, maintainable architecture that can continue beyond the hackathon.

---
