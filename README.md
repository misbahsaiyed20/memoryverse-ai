# 🚀 MemoryVerse AI

> **An AI-Powered Digital Identity System**
>
> MemoryVerse AI transforms scattered academic and professional documents into an intelligent, searchable knowledge repository using AI, Knowledge Graphs, Vector Search, and Retrieval-Augmented Generation (RAG).

---

## 📖 Overview

Throughout a student's academic and professional journey, important documents such as certificates, resumes, internship letters, project reports, portfolios, and achievements become scattered across folders, emails, and cloud drives.

MemoryVerse AI automatically understands, organizes, connects, and retrieves this information, allowing users to build a **digital identity** instead of just storing files.

This project was developed for **MemoryVerse AI '26 Hackathon**.

---

# ✨ Features

### 📂 AI Document Ingestion

- Upload Certificates
- Upload Resumes
- Upload Internship Letters
- Upload Project Reports
- Upload Academic Documents
- Secure file storage

---

### 🧠 Intelligent Processing

After upload, the system automatically:

- Processes documents
- Extracts text
- Splits documents into semantic chunks
- Generates vector embeddings
- Extracts structured entities using Gemini AI

---

### 🏷 Intelligent Categorization

MemoryVerse AI automatically identifies:

- Skills
- Technologies
- Projects
- Certifications
- Achievements
- Organizations
- Education
- Internships

---

### 🔗 Knowledge Graph

Extracted entities are stored as:

- Knowledge Nodes
- Knowledge Relationships (Edges)

This enables the system to understand connections such as:

```
Python
      │
      ▼
Machine Learning Project
      │
      ▼
AI Internship
```

---

### 🔍 Semantic Search

Instead of keyword matching, MemoryVerse AI performs semantic search using vector embeddings.

Example queries:

- Show all my AI projects
- Show Python certifications
- Show internship documents
- Show React projects
- Show my latest resume

---

### 🤖 Verse AI Assistant

Users can ask natural language questions like:

> What projects have I completed?

> What certifications do I have?

> What skills should I improve?

Verse AI answers using Retrieval-Augmented Generation (RAG) grounded in the user's uploaded documents.

---

### 📊 Dashboard

Provides an overview of:

- Uploaded Documents
- Processing Status
- Knowledge Statistics
- Technology Distribution
- Top Skills
- Recent Documents

---

### 🧠 Career Brain

Automatically builds a structured career profile including:

- Skills
- Projects
- Technologies
- Certifications
- Achievements
- Organizations
- Internships

---

### 📅 Timeline

Visualizes the user's academic and professional journey chronologically.

Example:

```
2023
│
├── Python Certification

2024
│
├── Machine Learning Project

2025
│
├── AI Internship
```

---

### 🕸 Knowledge Graph Visualization

Displays relationships between extracted entities through an interactive graph.

---

# 🏗 System Architecture

```
                User

                  │

          Upload Documents

                  │

          FastAPI Backend

                  │

        Document Processing

                  │

            Text Extraction

                  │

             Chunking Engine

                  │

        Google Gemini AI

                  │

      Entity & Relation Extraction

                  │

        Knowledge Graph Builder

          ┌──────────────┐
          │ PostgreSQL   │
          └──────────────┘

                  │

            Embeddings

                  │

             ChromaDB

                  │

        Retrieval (Semantic Search)

                  │

             Verse AI (RAG)

                  │

       Dashboard • Timeline
      Career Brain • Search
```

---

# 🛠 Tech Stack

## Frontend

- Next.js 15
- React
- TypeScript
- Tailwind CSS
- Shadcn UI

---

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

---

## AI & Machine Learning

- Google Gemini API
- Retrieval-Augmented Generation (RAG)
- Knowledge Graph
- NLP
- Semantic Chunking
- Vector Embeddings

---

## Vector Database

- ChromaDB

---

## Authentication

- Firebase Authentication
- Google Sign-In

---

## Storage

- Local Document Storage

---

# 📁 Project Structure

```
memoryverse-ai
│
├── frontend/
│
├── backend/
│   ├── app/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── extraction/
│   ├── search/
│   ├── embeddings/
│   └── db/
│
├── uploads/
├── chromadb/
└── sql/
```

---

# ⚙ Installation

## Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Database

Create PostgreSQL database:

```
memoryverse
```

Run required SQL migration scripts.

---

# 🔄 Workflow

```
Upload Document
        │
        ▼
Document Processing
        │
        ▼
Chunk Generation
        │
        ▼
Gemini AI Extraction
        │
        ▼
Knowledge Graph
        │
        ▼
Embeddings
        │
        ▼
ChromaDB
        │
        ▼
Semantic Search
        │
        ▼
Verse AI
```

---

# 💡 AI Concepts Used

- Natural Language Processing (NLP)
- Retrieval-Augmented Generation (RAG)
- Knowledge Graph
- Entity Extraction
- Semantic Search
- Vector Embeddings
- Similarity Search
- AI-powered Document Understanding

---

# 📸 Screenshots

Add screenshots of:

- Login Page
- Dashboard
- Upload Page
- Career Brain
- Timeline
- Knowledge Graph
- Semantic Search
- Verse AI

---

# 🚀 Future Improvements

- Cloud Deployment
- Resume Generation
- Interview Preparation
- Skill Gap Analysis
- Learning Recommendations
- Multi-language Support
- OCR for Scanned Documents
- Real-time Collaboration

---

# 👩‍💻 Developed By

**Misba Saiyed**

GitHub:
https://github.com/misbahsaiyed20

---

# 🙏 Acknowledgements

- Google Gemini AI
- ChromaDB
- FastAPI
- Next.js
- PostgreSQL
- Firebase Authentication
- MemoryVerse AI '26 Hackathon

---

# 📜 License

This project was developed for educational and hackathon purposes.