# 🏦 TITAN: Autonomous Financial Intelligence Platform

**TITAN** is an advanced Multi-Agent System designed to perform deep financial analysis and audit tasks on SEC 10-K filings. Powered by **LangGraph**, **FastAPI**, and **Vector Search**, it automates the retrieval, reasoning, and reporting of complex financial data.

---

## 🏗️ Architecture & Tech Stack

TITAN is built following **Clean Architecture** principles and modern MLOps practices:

- **Core Backend:** Python 3.12+, FastAPI (Async), SQLModel.
- **Orchestration:** LangGraph (Cyclic Agentic Flows).
- **Database:** PostgreSQL 16 + `pgvector` (Dockerized).
- **Data Engineering:** `sec-edgar-downloader`, BeautifulSoup4 (Custom Parsing).
- **Inference:** Local LLMs (Ollama) & Cloud Fallbacks.
- **Vector Search:** SentenceTransformers (All-MiniLM/MPNet) with GPU Acceleration (CUDA).
- **Infrastructure:** Docker Compose, Poetry.

---

## 🚀 Quick Start

### 1\. Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Poetry (Dependency Manager)
- NVIDIA GPU (Optional, for accelerated vectorization)

### 2\. Installation

    # Clone the repository
    git clone https://github.com/rauldgarcia/titan-platform.git
    cd titan-platform

    # Install dependencies
    poetry install

    # Start Infrastructure (Postgres + pgvector + pgAdmin)
    # Note: This automatically initializes the DB and activates vector extensions.
    sudo docker compose up -d

### 3\. Run the API

    poetry run uvicorn app.main:app --reload

- **Health Check:** `http://localhost:8000/health`
- **Docs:** `http://localhost:8000/docs`

---

## 📊 Data Pipeline (RAG Ingestion)

TITAN includes a specialized ETL pipeline to ingest, normalize, and vectorize financial data from the SEC EDGAR database.

### Phase 1: Extraction (Download)

Downloads the latest 10-K filings for target companies (e.g., AAPL, TSLA, MSFT).

    poetry run python scripts/ingest/download_sec.py

_Artifacts are stored in `data/sec_filings/` (Git ignored)._

### Phase 2: Transformation (Refinery)

Cleanses raw HTML, removing noise (scripts, styles) while preserving tabular structure and semantic paragraphs.

    poetry run python scripts/ingest/clean_data.py

_Cleaned text files are stored in `data/processed/`._

### Phase 3: Loading (Vectorization)

Chunks the cleaned text, generates embeddings using `sentence-transformers` (CUDA-enabled), and persists them into PostgreSQL.

    poetry run python scripts/ingest/vectorize.py

- **Model:** `all-mpnet-base-v2` (768 dimensions).
- **Chunking Strategy:** Recursive Character Split (1000 chars, 150 overlap).

---

## 🗺️ Project Roadmap

- \[x\] **Phase 1: Foundation**
  - \[x\] Environment Setup (Poetry, Docker, Git).
  - \[x\] Async Database Layer (Postgres + pgvector).
  - \[x\] Robust Configuration Management.
- \[x\] **Phase 2: Data Engineering**
  - \[x\] SEC Downloader Script.
  - \[x\] HTML-to-Text Parser (BeautifulSoup).
- \[x\] **Phase 3: The Brain (Vector Store)**
  - \[x\] Local Embedding Generation (GPU Accelerated).
  - \[x\] Vector Database Ingestion strategy (Batch Processing).
  - \[ \] Semantic Search Endpoint (Next Step).
- \[ \] **Phase 4: Agentic Workflow**
  - \[ \] LangGraph State Definition.
  - \[ \] "Analyst" & "Reporter" Agents.

---

## 🛡️ License

Private Portfolio Project - Raúl Daniel García Ramón.
