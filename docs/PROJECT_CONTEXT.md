# MemoryVerse AI – Project Context

**Project Name:** MemoryVerse AI

**Project Type:** AI-Powered Digital Identity & Knowledge Repository

**Current Status:** Active Development

**Architecture Owner:** ChatGPT

**Implementation:** Claude (following architecture and implementation rules)

---

# 1. Project Vision

MemoryVerse AI is an AI-powered digital identity platform that transforms fragmented academic and professional records into a structured, searchable knowledge repository.

Instead of treating uploaded documents as isolated files, the system extracts knowledge from them and builds a connected "Career Brain" that represents a user's education, skills, projects, internships, certifications, achievements, work experience, and other career-related information.

The long-term goal is to create an AI assistant capable of answering career-related questions using verified evidence from the user's own documents instead of generating unsupported responses.

---

# 2. Problem Statement

Students and professionals accumulate information across many different documents such as:

- Resumes
- Certificates
- Transcripts
- Project Reports
- Internship Letters
- Research Papers
- Recommendation Letters
- Portfolios

Finding information later becomes difficult because these files remain disconnected.

MemoryVerse AI converts those documents into structured knowledge that can be searched, connected, and explained with supporting evidence.

---

# 3. Core Objectives

The project aims to:

- Store documents securely.
- Process uploaded files into plain text.
- Split documents into meaningful chunks.
- Generate vector embeddings for semantic search.
- Build a structured knowledge graph.
- Link extracted knowledge back to original evidence.
- Allow intelligent semantic search.
- Support future AI conversations grounded in verified evidence.

---

# 4. High-Level Architecture

The overall document processing pipeline is:

```
User

↓

Firebase Authentication

↓

Upload Document

↓

Local Storage

↓

PostgreSQL Metadata

↓

Document Processing

↓

Chunk Generation

↓

Gemini Knowledge Extraction

↓

Knowledge Graph

↓

Evidence Links

↓

Gemini Embeddings

↓

ChromaDB

↓

Semantic Search

↓

Future Verse AI Assistant
```

---

# 5. System Components

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- Firebase Authentication
- Dashboard
- Document Upload Interface

---

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Background Tasks
- Modular Service Architecture

---

## AI Components

### Gemini

Used for:

- Knowledge extraction
- Structured entity extraction
- Relationship generation
- Embedding generation

Gemini is **never** treated as the source of truth.

---

### ChromaDB

Stores only:

- Vector embeddings
- Chunk metadata

ChromaDB is used exclusively for semantic retrieval.

---

### PostgreSQL

PostgreSQL is the system's source of truth.

It stores:

- Users
- Documents
- Chunks
- Knowledge Nodes
- Knowledge Edges
- Evidence Links

No permanent business data is stored inside ChromaDB.

---

# 6. Career Brain

Career Brain is the structured knowledge representation of a user's career.

It consists of:

- Skills
- Projects
- Education
- Experience
- Certifications
- Organizations
- Achievements
- Technical Concepts

These entities are connected using relationships inside the knowledge graph.

---

# 7. Evidence-First Architecture

Every extracted fact should be traceable back to the original uploaded document.

Knowledge is never accepted without supporting evidence.

This architecture minimizes hallucination and improves trustworthiness.

---

# 8. Search Architecture

The search pipeline is:

```
User Query

↓

Gemini Query Embedding

↓

ChromaDB Vector Search

↓

Relevant Chunks

↓

Evidence Retrieval

↓

Future AI Response
```

Search retrieves document chunks using embeddings instead of keyword matching.

---

# 9. Design Principles

The project follows these principles:

- PostgreSQL is the source of truth.
- ChromaDB stores only embeddings.
- AI never replaces stored data.
- Every knowledge item should be evidence-backed.
- Services should have a single responsibility.
- Infrastructure should be replaceable through abstractions.
- Business logic should remain independent of third-party libraries.
- Existing architecture should be extended instead of rewritten whenever possible.

---

# 10. Technology Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Firebase Client SDK

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

## AI

- Google Gemini
- Gemini Embeddings

## Vector Database

- ChromaDB

## Authentication

- Firebase Authentication

## Storage

- Local Storage (current)
- Cloud storage planned for future

---

# 11. Current Capabilities

The project currently supports:

- User authentication
- Document upload
- Document metadata storage
- Document processing
- Text chunking
- Gemini knowledge extraction
- Knowledge graph generation
- Evidence linking
- Embedding generation
- Semantic search

---

# 12. Future Roadmap

Planned features include:

- Conversational Verse AI Assistant
- Hybrid Retrieval (Graph + Vector Search)
- Timeline Visualization
- Career Analytics
- Skill Gap Detection
- Resume Generation
- Portfolio Generation
- Career Recommendations
- Interview Preparation
- Cloud Deployment

---

# 13. Architecture Philosophy

MemoryVerse AI follows an evidence-driven AI architecture.

The database remains the permanent source of truth.

AI is used only for reasoning, extraction, embeddings, and retrieval.

Every response generated by future AI components should be explainable using evidence from the user's uploaded documents.

The architecture is designed to be modular, maintainable, extensible, and suitable for future production deployment.