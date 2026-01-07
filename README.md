# 🏦 TITAN: Autonomous Financial Intelligence Platform

[![LangSmith](https://img.shields.io/badge/Observability-LangSmith-blue?style=flat&logo=langchain)](https://smith.langchain.com/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-FF4B4B?style=flat&logo=langchain&logoColor=white)](https://python.langchain.com/docs/langgraph)
[![MCP](https://img.shields.io/badge/Integration-MCP-4B32C3?style=flat&logo=anthropic&logoColor=white)](https://modelcontextprotocol.io/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Postgres](https://img.shields.io/badge/DB-PostgreSQL_16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tailwind](https://img.shields.io/badge/UI-TailwindCSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

**TITAN** is an advanced Multi-Agent System designed to perform deep financial analysis and audit tasks on SEC 10-K filings. It employs a **Hierarchical Agentic Architecture** powered by LangGraph, where a Supervisor delegates tasks to specialized workers (Research, Quant, Market Data, Reporting).

---

## 🧠 Agentic Architecture (The "Deep Analyzer")

TITAN utilizes a **Supervisor-Worker** topology with **Model Context Protocol (MCP)** integration. The Supervisor orchestrates a team of agents, maintaining a feedback loop until the analysis is comprehensive.

```mermaid
    graph TD
        User[User Request] --> Supervisor{SUPERVISOR NODE}

        Supervisor -- "Need History/Risks" --> Research[Research Agent]
        Supervisor -- "Need Math/Ratios" --> Quant[Quant Agent]
        Supervisor -- "Need Live Price" --> Market[Market Agent]
        Supervisor -- "Analysis Complete" --> Reporter[Reporter Agent]

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

        subgraph "Market Data (MCP)"
            Market --> Client[MCP Client]
            Client <--> Server[Yahoo Finance Server]
            Client --> Return3[Return Live Data]
        end

        Return1 --> Supervisor
        Return2 --> Supervisor
        Return3 --> Supervisor

        Reporter --> HTML[HTML Dashboard] --> End((End))
```

---

## 🧪 Analysis Capabilities & Examples

TITAN can handle various types of financial queries, from simple retrieval to complex multi-step reasoning.

### 1\. Deep Strategic Analysis (RAG + Reasoning)

    "Analyze the key risk factors and strategic outlook for Apple (AAPL) based on their latest 10-K."

### 2\. Quantitative Analysis (RAG + Python Calculation)

    "Based on Microsoft's revenue and total debt mentioned in the report, calculate the Debt-to-Revenue ratio."

### 3\. Real-Time Market Insight (MCP Integration)

    "What is the current stock price of NVIDIA and its market cap right now?"

### 4\. Hybrid Reasoning (The "Deep Analyzer")

    "Get the current price of Tesla using market tools, then compare it with the risks mentioned in their annual report. Is the market sentiment aligned with their operational risks?"

---

## 🏗️ Architecture & Tech Stack

- **Core Backend:** Python 3.12+, FastAPI (Async), SQLModel.
- **Orchestration:** LangGraph (Hierarchical StateGraph with PostgreSQL Persistence).
- **Connectivity:** **Model Context Protocol (MCP)** client/server architecture for external data.
- **Database:** PostgreSQL 16 + `pgvector` (Dockerized).
- **Inference:** Local LLMs via **Ollama** (Llama 3.2).
- **Tools:**
  - **Yahoo Finance (MCP):** Real-time market data server.
  - **Tavily AI:** Web Search fallback.
  - **Python REPL:** Sandboxed code execution.
- **Reporting:** Jinja2 + TailwindCSS (Glassmorphism UI).

---

## 🗺️ Project Roadmap

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
- **Phase 5: Advanced Orchestration (The "Deep Analyzer")**
  - \[x\] **Persistent Memory:** Replace in-memory checkpointer with PostgreSQL persistence (Long-running threads).
  - \[x\] **Hierarchical Agents:** Implement a "Supervisor" node to delegate tasks.
  - \[x\] **Quantitative Tool:** Connect Python REPL for real-time financial calculations.
  - \[x\] **Model Context Protocol (MCP):** Integrate custom Yahoo Finance server for real-time market data.

### 🚧 In Progress & Future Steps

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
