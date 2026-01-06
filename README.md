# 🏦 TITAN: Autonomous Financial Intelligence Platform

[![LangSmith](https://img.shields.io/badge/Observability-LangSmith-blue?style=flat&logo=langchain)](https://smith.langchain.com/) [![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-FF4B4B?style=flat&logo=langchain&logoColor=white)](https://python.langchain.com/docs/langgraph) [![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![Postgres](https://img.shields.io/badge/DB-PostgreSQL_16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![Tailwind](https://img.shields.io/badge/UI-TailwindCSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

**TITAN** is an advanced Multi-Agent System designed to perform deep financial analysis and audit tasks on SEC 10-K filings. Powered by **LangGraph**, **FastAPI**, and **Vector Search**, it automates the retrieval, reasoning, and reporting of complex financial data into professional HTML Dashboards.

---

## 🧠 Agentic Architecture (Self-Correcting RAG)

TITAN implements a **Corrective RAG (CRAG)** workflow with logic to fallback to external search if internal data is insufficient.

```mermaid
    graph TD
        A[Start Request] --> B[Retrieve Node]
        B -->|Fetch 10-K Chunks| C[Grade Node]
        C -->|Evaluate Relevance| D{Decision?}
        D -- Relevant --> E[Generate Report]
        D -- Not Relevant --> F[Web Search Node]
        F -->|Fetch Live Data| E
        E -->|Render HTML| G[End Response]
```

---

## 🏗️ Architecture & Tech Stack

TITAN is built following **Clean Architecture** principles and modern MLOps practices:

- **Core Backend:** Python 3.12+, FastAPI (Async), SQLModel.
- **Orchestration:** LangGraph (Cyclic Agentic Flows).
- **Persistence:** PostgreSQL + `psycopg-pool` (Async Connection Pooling for long-term agent memory).
- **Database:** PostgreSQL 16 + `pgvector` (Dockerized).
- **Data Engineering:** `sec-edgar-downloader`, BeautifulSoup4.
- **Inference:** Local LLMs via **Ollama** (Llama 3.2).
- **Tools:** **Tavily AI** (Web Search Fallback).
- **Observability:** **LangSmith** (Tracing & Monitoring).
- **Reporting Engine:** Jinja2 + TailwindCSS.

---

## 🚀 Quick Start

### 1\. Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Poetry
- **Ollama** running locally.

### 2\. Setup

    # Clone the repository
    git clone https://github.com/rauldgarcia/titan-platform.git
    cd titan-platform

    # Install dependencies
    poetry install

    # Configure Secrets (.env)
    # TAVILY_API_KEY=tvly-xxxx
    # LANGCHAIN_API_KEY=lsv2_xxxx

    # Start Infrastructure
    sudo docker compose up -d

### 3\. Run the API

    poetry run uvicorn app.main:app --reload

---

### ✅ Completed Phases

- **Phase 1: Foundation**
  - \[x\] Environment Setup (Poetry, Docker, Git).
  - \[x\] Async Database Layer (Postgres + pgvector).
- **Phase 2: Data Engineering (ETL)**
  - \[x\] SEC Downloader Script.
  - \[x\] HTML-to-Text Parser (BeautifulSoup).
  - \[x\] GPU-Accelerated Vectorization (SentenceTransformers).
- **Phase 3: The Brain (Inference)**
  - \[x\] Semantic Search Service (Cosine Similarity).
  - \[x\] RAG Integration with Local LLMs (Ollama).
- **Phase 4: Agentic Workflow v1**
  - \[x\] LangGraph State Definition.
  - \[x\] Self-Correction Logic (Document Grader).
  - \[x\] Web Search Fallback (Tavily).
  - \[x\] **Reporting Engine:** Jinja2 + TailwindCSS HTML Generation.
  - \[x\] **Refactoring:** Centralized Prompts & Clean Architecture.

### 🚧 In Progress & Future Steps

- **Phase 5: Advanced Orchestration (The "Deep Analyzer")**
  - \[x\] **Persistent Memory:** Replace in-memory checkpointer with PostgreSQL persistence (Long-running threads).
  - \[ \] **Hierarchical Agents:** Implement a "Supervisor" node to delegate tasks.
  - \[ \] **Quantitative Tool:** Connect Python REPL for real-time financial calculations (Ratios, Growth rates).
- **Phase 6: MLOps & Quality Engineering**
  - \[ \] **Unit & Integration Testing:** Comprehensive Pytest suite for agents and API.
  - \[ \] **CI/CD Pipelines:** GitHub Actions for automated linting, testing, and Docker builds.
  - \[ \] **Evaluation:** Implement RAGAS to measure retrieval accuracy and hallucination rates.
- **Phase 7: Full Stack Experience**
  - \[ \] **Frontend Client:** React Application for chat interface and report visualization.
  - \[ \] **Cloud Deployment:** Deploy backend to GCP Cloud Run.

---

## 🛡️ License

Private Portfolio Project - Raúl Daniel García Ramón.
