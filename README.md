# 🏦 TITAN: Autonomous Financial Intelligence Platform

[![LangSmith](https://img.shields.io/badge/Observability-LangSmith-blue?style=flat&logo=langchain)](https://smith.langchain.com/) [![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![Postgres](https://img.shields.io/badge/DB-PostgreSQL_16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![Tailwind](https://img.shields.io/badge/UI-TailwindCSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

**TITAN** is an advanced Multi-Agent System designed to perform deep financial analysis and audit tasks on SEC 10-K filings. Powered by **LangGraph**, **FastAPI**, and **Vector Search**, it automates the retrieval, reasoning, and reporting of complex financial data into professional HTML Dashboards.

---

## 🏗️ Architecture & Tech Stack

TITAN is built following **Clean Architecture** principles and modern MLOps practices:

- **Core Backend:** Python 3.12+, FastAPI (Async), SQLModel.
- **Orchestration:** LangGraph (Cyclic Agentic Flows).
- **Database:** PostgreSQL 16 + `pgvector` (Dockerized).
- **Data Engineering:** `sec-edgar-downloader`, BeautifulSoup4.
- **Inference:** Local LLMs via **Ollama** (Llama 3.2).
- **Tools:** **Tavily AI** (Web Search Fallback).
- **Observability:** **LangSmith** (Tracing & Monitoring).
- **Reporting Engine:** Jinja2 + TailwindCSS (Enterprise-grade HTML Generation).

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

## 🤖 Agentic Workflow (Self-Correcting RAG)

TITAN implements a \*\*Corrective RAG (CRAG)\*\* architecture with web fallback capabilities.

### Endpoint: `POST /chat/agent`

1.  **Retrieve:** Fetches semantic chunks from PostgreSQL.
2.  **Grade:** Filter irrelevant documents.
3.  **Decision (Conditional Edge):** Uses DB context OR falls back to Web Search (Tavily).
4.  **Report Generation:**

    - Extracts structured JSON (Risks, Outlook, Summary) using strict output parsers.
    - Renders a **"Glassmorphism" Dashboard** using Jinja2 templates.

    // Request
    {
    "question": "Analyze the risk factors and strategic outlook for Apple",
    "thread_id": "session_123"
    }
    // Returns: A full HTML Rendered Report with tables and KPIs.

---

## 📊 Data Pipeline

- **Extraction:** `scripts/ingest/download_sec.py`
- **Transformation:** `scripts/ingest/clean_data.py`
- **Vectorization:** `scripts/ingest/vectorize.py` (GPU Accelerated)

---

## 🗺️ Project Roadmap

- \[x\] **Phase 1: Foundation** (DB, Docker, Async Config).
- \[x\] **Phase 2: Data Engineering** (ETL, SEC Parsing).
- \[x\] **Phase 3: The Brain** (Vector Search, Embeddings).
- \[x\] **Phase 4: Agentic Workflow** (LangGraph, Self-Correction, Web Search).
- \[x\] **Phase 5: Reporting Engine**
  - \[x\] Structured Output (Pydantic to JSON).
  - \[x\] Jinja2 + TailwindCSS HTML Rendering.
- \[ \] **Phase 6: Production Hardening**
  - \[ \] PostgreSQL Persistence (Long-term Memory).
  - \[ \] Prompts Refactoring & Centralization.
  - \[ \] Comprehensive Testing (Pytest).

---

## 🛡️ License

Private Portfolio Project - Raúl Daniel García Ramón.
