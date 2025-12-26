# 🏦 TITAN: Autonomous Financial Intelligence Platform

**TITAN** is an advanced Multi-Agent System designed to perform deep financial analysis and audit tasks on SEC 10-K filings. Powered by **LangGraph**, **FastAPI**, and **Vector Search**, it automates the retrieval, reasoning, and reporting of complex financial data.

---

## 🏗️ Architecture & Tech Stack

TITAN is built following **Clean Architecture** principles and modern MLOps practices:

- **Core Backend:** Python 3.12+, FastAPI (Async), SQLModel.
- **Orchestration:** LangGraph (Cyclic Agentic Flows).
- **Database:** PostgreSQL 16 + `pgvector` (Dockerized).
- **Data Engineering:** `sec-edgar-downloader`, BeautifulSoup4 (Custom Parsing).
- **Inference:** Local LLMs via **Ollama** (Llama 3.2 / Mistral).
- **Vector Search:** SentenceTransformers (CUDA) + Cosine Similarity Search.
- **Infrastructure:** Docker Compose, Poetry.

---

## 🚀 Quick Start

### 1\. Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Poetry
- **Ollama** installed and running.

### 2\. Installation

    # Clone the repository
    git clone https://github.com/rauldgarcia/titan-platform.git
    cd titan-platform

    # Install dependencies
    poetry install

    # Pull the Local LLM (Required for RAG)
    ollama pull llama3.2

    # Start Infrastructure (Postgres + pgvector + pgAdmin)
    sudo docker compose up -d

### 3\. Run the API

    # Ensure Ollama is running in background: 'ollama serve'
    poetry run uvicorn app.main:app --reload

- **Swagger UI:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

---

## 🤖 RAG Interface (Chat)

You can interact with the ingested financial data via the REST API.

### Endpoint: `POST /chat/simple`

Performs semantic search on the vector database and generates a grounded response using the local LLM.

    // Request Body
    {
      "question": "What are the primary risk factors for Tesla?"
    }



    // Response
    {
      "answer": "According to Tesla's 10-K, primary risks include competition in the EV market...",
      "sources": ["TSLA (chunk_45)", "TSLA (chunk_102)"]
    }

---

## 📊 Data Pipeline (ETL)

### Phase 1: Extraction

    poetry run python scripts/ingest/download_sec.py

### Phase 2: Transformation

    poetry run python scripts/ingest/clean_data.py

### Phase 3: Loading (Vectorization)

    poetry run python scripts/ingest/vectorize.py

---

## 🗺️ Project Roadmap

- \[x\] **Phase 1: Foundation**
  - \[x\] Environment Setup (Poetry, Docker, Git).
  - \[x\] Async Database Layer (Postgres + pgvector).
  - \[x\] Robust Configuration Management.
- \[x\] **Phase 2: Data Engineering**
  - \[x\] SEC Downloader Script.
  - \[x\] HTML-to-Text Parser.
- \[x\] **Phase 3: The Brain (Vector Store)**
  - \[x\] GPU-Accelerated Vectorization.
  - \[x\] Semantic Search Service (Cosine Similarity).
  - \[x\] RAG Inference Endpoint (Ollama Integration).
- \[ \] **Phase 4: Agentic Workflow**
  - \[ \] LangGraph State Definition.
  - \[ \] "Analyst" & "Reporter" Agents.
  - \[ \] Self-Reflection Loop.

---

## 🛡️ License

Private Portfolio Project - Raúl Daniel García Ramón.
