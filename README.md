# 🏦 TITAN: Autonomous Financial Intelligence Platform

[![LangSmith](https://img.shields.io/badge/Observability-LangSmith-blue?style=flat&logo=langchain)](https://smith.langchain.com/) [![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-FF4B4B?style=flat&logo=langchain&logoColor=white)](https://python.langchain.com/docs/langgraph) [![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![Postgres](https://img.shields.io/badge/DB-PostgreSQL_16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![Tailwind](https://img.shields.io/badge/UI-TailwindCSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

**TITAN** is an advanced Multi-Agent System designed to perform deep financial analysis and audit tasks on SEC 10-K filings. It employs a **Hierarchical Agentic Architecture** powered by LangGraph, where a Supervisor delegates tasks to specialized workers (Research, Quant, Reporting).

---

## 🧠 Agentic Architecture (The "Deep Analyzer")

TITAN has evolved from a linear RAG into a **Supervisor-Worker** topology. A central orchestrator creates a plan and loops through specialized agents until the analysis is complete.

    graph TD
        User[User Request] --> Supervisor{SUPERVISOR NODE}

        Supervisor -- "Need Info" --> Research[Research Agent]
        Supervisor -- "Need Math" --> Quant[Quant Agent]
        Supervisor -- "Analysis Done" --> Reporter[Reporter Agent]

        subgraph "Research Branch"
            Research --> DB[Vector DB]
            DB --> Grade{Relevance?}
            Grade -- Poor --> Web[Web Search]
            Grade -- Good --> Return1[Return Findings]
            Web --> Return1
        end

        subgraph "Quant Branch"
            Quant --> Code[Python REPL]
            Code --> Return2[Return Calculation]
        end

        Return1 --> Supervisor
        Return2 --> Supervisor

        Reporter --> HTML[HTML Dashboard] --> End((End))

---

## 🏗️ Architecture & Tech Stack

- **Core Backend:** Python 3.12+, FastAPI (Async), SQLModel.
- **Orchestration:** LangGraph (Hierarchical StateGraph with PostgreSQL Persistence).
- **Database:** PostgreSQL 16 + `pgvector` (Dockerized).
- **Data Engineering:** `sec-edgar-downloader`, BeautifulSoup4.
- **Inference:** Local LLMs via **Ollama** (Llama 3.2).
- **Tools:**
  - **Tavily AI:** Real-time Web Search.
  - **Python REPL:** Sandboxed code execution for precise financial math.
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

## 🗺️ Project Roadmap

- \[x\] **Phase 1: Foundation** (DB, Docker, Async Config).
- \[x\] **Phase 2: Data Engineering** (ETL, SEC Parsing).
- \[x\] **Phase 3: The Brain** (Vector Search, Embeddings).
- \[x\] **Phase 4: Agentic Workflow v1** (Self-Correction, Web Search).
- \[x\] **Phase 5: Advanced Orchestration (The "Deep Analyzer")**
  - \[x\] **Supervisor Node:** Central router for multi-agent delegation.
  - \[x\] **Quant Agent:** Python REPL integration for math operations.
  - \[x\] **Circuit Breaker:** Logic to prevent infinite reasoning loops.
  - \[x\] **Persistent Memory:** Postgres-backed thread persistence.
- \[ \] **Phase 6: MLOps & Quality Engineering**
  - \[ \] **Unit & Integration Testing:** Comprehensive Pytest suite.
  - \[ \] **CI/CD Pipelines:** GitHub Actions.
  - \[ \] **Evaluation:** RAGAS metrics implementation.
- \[ \] **Phase 7: Full Stack Experience**
  - \[ \] **Frontend Client:** React Application.
  - \[ \] **Cloud Deployment:** GCP Cloud Run.

---

## 🛡️ License

Private Portfolio Project - Raúl Daniel García Ramón.
