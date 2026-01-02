# 🏦 TITAN: Autonomous Financial Intelligence Platform

**TITAN** is an advanced Multi-Agent System designed to perform deep financial analysis and audit tasks on SEC 10-K filings. Powered by **LangGraph**, **FastAPI**, and **Vector Search**, it automates the retrieval, reasoning, and reporting of complex financial data.

---

## 🏗️ Architecture & Tech Stack

TITAN is built following **Clean Architecture** principles and modern MLOps practices:

- **Core Backend:** Python 3.12+, FastAPI (Async), SQLModel.
- **Orchestration:** LangGraph (Cyclic Agentic Flows).
- **Database:** PostgreSQL 16 + `pgvector` (Dockerized).
- **Data Engineering:** `sec-edgar-downloader`, BeautifulSoup4 (Custom Parsing).
- **Inference:** Local LLMs via **Ollama** (Llama 3.2).
- **Tools:** **Tavily AI** (Optimized Web Search for Agents).
- **Infrastructure:** Docker Compose, Poetry.

---

## 🚀 Quick Start

### 1\. Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Poetry
- **Ollama** running locally.
- **Tavily API Key** (for web search fallback).

### 2\. Setup

    # Clone the repository
    git clone https://github.com/rauldgarcia/titan-platform.git
    cd titan-platform

    # Install dependencies
    poetry install

    # Configure Secrets (.env)
    # Add TAVILY_API_KEY=tvly-xxxx

    # Start Infrastructure
    sudo docker compose up -d

### 3\. Run the API

    poetry run uvicorn app.main:app --reload

---

## 🤖 Agentic Workflow (Self-Correcting RAG)

TITAN implements a \*\*Corrective RAG (CRAG)\*\* architecture with web fallback capabilities.

### Endpoint: `POST /chat/agent`

The graph executes the following logic:

1.  **Retrieve:** Fetches semantic chunks from PostgreSQL (10-K Filings).
2.  **Grade:** A specialized Agent evaluates if the retrieved documents are relevant to the question.
3.  **Decision Node (Conditional Edge):**
    - ✅ **If Relevant:** Proceeds to **Generate** answer using internal data.
    - ⚠️ **If Irrelevant/Empty:** Triggers **Web Search** (Tavily) to find real-time or missing info.
4.  **Generate:** Synthesizes the final answer using the best available context (Internal vs External).

    // Request
    {
    "question": "What is the current stock price of Apple?"
    }
    // Logic: DB has 2024 data (Irrelevant) -> Falls back to Web Search -> Returns real-time price.

---

## 📊 Data Pipeline

- **Extraction:** `poetry run python scripts/ingest/download_sec.py`
- **Transformation:** `poetry run python scripts/ingest/clean_data.py`
- **Vectorization:** `poetry run python scripts/ingest/vectorize.py` (GPU Accelerated)

---

## 🗺️ Project Roadmap

- \[x\] **Phase 1: Foundation**
  - \[x\] Async Database Layer (Postgres + pgvector).
- \[x\] **Phase 2: Data Engineering**
  - \[x\] SEC ETL Pipeline.
- \[x\] **Phase 3: The Brain (Vector Store)**
  - \[x\] Semantic Search Service.
- \[x\] **Phase 4: Agentic Workflow**
  - \[x\] LangGraph State & Nodes.
  - \[x\] Document Grader (Relevance Filter).
  - \[x\] **Web Search Fallback (Tavily Integration).**
  - \[ \] "Reporter" Agent (Jinja2 Output) - _Next Step_.

---

## 🛡️ License

Private Portfolio Project - Raúl Daniel García Ramón.
