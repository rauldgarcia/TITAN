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
- **Ollama** running locally.

### 2\. Installation

    # Clone the repository
    git clone https://github.com/rauldgarcia/titan-platform.git
    cd titan-platform

    # Install dependencies
    poetry install

    # Start Infrastructure (Postgres + pgvector + pgAdmin)
    sudo docker compose up -d

### 3\. Run the API

    # Ensure Ollama is running in background
    poetry run uvicorn app.main:app --reload

---

## 🤖 Agentic Workflow (LangGraph)

TITAN uses a graph-based architecture to ensure high-quality responses.

### Endpoint: `POST /chat/agent`

Executes the **Corrective RAG (CRAG)** workflow:

1.  **Retrieve:** Fetches semantic chunks from PostgreSQL.
2.  **Grade:** A specialized LLM agent evaluates each document for relevance, filtering out noise.
3.  **Generate:** Synthesizes the final answer using only high-quality context.

    // Request
    {
    "question": "What is the revenue of Apple and does the document mention 'Risk Factors'?"
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
- \[x\] **Phase 2: Data Engineering**
  - \[x\] SEC Downloader & Parser.
- \[x\] **Phase 3: The Brain (Vector Store)**
  - \[x\] GPU-Accelerated Vectorization.
  - \[x\] Semantic Search Service.
- \[ \] **Phase 4: Agentic Workflow**
  - \[x\] LangGraph State Definition.
  - \[x\] Document Grader Node (Relevance Filter).
  - \[ \] Search Fallback (Web Search).
  - \[ \] "Reporter" Agent (Jinja2 Output).

---

## 🛡️ License

Private Portfolio Project - Raúl Daniel García Ramón.
