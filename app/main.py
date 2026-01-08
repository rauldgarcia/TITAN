import os
from dotenv import load_dotenv
import logging
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import init_db, get_session
from app.services.retriever import RetrievalService
from app.services.rag import RAGService
from app.agents.graph import TitanGraph
from app.core.db_pool import open_pool, close_pool

load_dotenv()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TITAN System: INITIATING...")
    try:
        await init_db()
        logger.info("System Ready.")
        await open_pool()
        logger.info("LangGraph Persistence Pool Ready.")
    except Exception as e:
        logger.error(f"Critical Startup Error: {e}")
    yield
    await close_pool()
    logger.info("TITAN System: SHUTTING DOWN...")

app = FastAPI(
    title="TITAN Platform",
    description="Financial Intelligence Multi-Agent System",
    version="0.1.0",
    lifespan=lifespan
)
templates = Jinja2Templates(directory="app/templates")
class ChatRequest(BaseModel):
    question: str

class AgentRequest(BaseModel):
    question: str
    thread_id: str = "default_thread"

class ResumeRequest(BaseModel):
    thread_id: str
    new_instructions: Optional[str] = None

@app.post("/chat/simple", tags=["Inference"])
async def simple_chat(request: ChatRequest, session: AsyncSession = Depends(get_session)):
    """
    Direct RAG endpoint (No Agents yet).
    Retrieves context -> Calls LLM -> Returns Answer.
    """
    retriever = RetrievalService(session)
    rag_engine = RAGService(retriever)

    result = await rag_engine.answer_question(request.question)
    return result

@app.post("/chat/agent", tags=["Inference"])
async def agent_chat(request: AgentRequest, session: AsyncSession = Depends(get_session)):
    """
    Stateful Agentic RAG with PostgreSQL Persistence.
    The 'thread_id' in the request determines the conversation history.
    """
    titan_system = TitanGraph(session)
    config = {
        "configurable": {"thread_id": request.thread_id},
        "recursion_limit": 50
        }

    agent = await titan_system.get()
    final_state = await agent.ainvoke({"question": request.question}, config)

    if final_state.get("next_step") == "human_intervention":
        return {
            "status": "PAUSED",
            "message": "Agent paused for human intervention.",
            "error": final_state.get("error_message")
        }

    return {
        "status": "COMPLETED",
        "answer": final_state.get("generation"),
        "sources": final_state.get("sources", [])
    }

@app.post("/agent/resume", tags=["Agent Control"])
async def resume_agent(request: ResumeRequest, session: AsyncSession = Depends(get_session)):
    """
    Resumes a paused agent. Allows injecting manual corrections.
    """
    titan = TitanGraph(session)
    agent = await titan.get()
    config = {"configurable": {"thread_id": request.thread_id}}

    current_state = await agent.aget_state(config)
    if not current_state.next:
        return {"message": "Thread is not paused or does not exist."}

    resume_input =None
    if request.new_instructions:
        resume_input = {
            "documents": [f"Manual Correction/Calculation: {request.new_instructions}"],
            "error_message": None,
            "next_step": "reporter_agent"
        }

    await agent.aupdate_state(config, resume_input)
    resume_input = None

    final_state = await agent.ainvoke(resume_input, config)

    return {
        "status": "Resumed",
        "answer": final_state.get("generation", "Processing completed.")
    }


@app.get("/health", tags=["System"])
async def health_check(session: AsyncSession = Depends(get_session)):
    """
    Endpoint to verify that the system works
    """
    try:
        result = await session.execute(text("SELECT 1"))
        return {
            "status": "active",
            "system": "TITAN",
            "database": "connected",
            "environment": "development",
            "db_check": result.scalar()
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "database": "unreachable",
            "detail": str(e)
        }

@app.get("/test-report", response_class=HTMLResponse, tags=["UI Debug"])
async def test_report_ui(request: Request):
    """
    Endpoint visual para probar el diseño del reporte sin ejecutar el agente.
    """
    # Datos Mock (Simulando lo que extraería el agente)
    mock_data = {
        "company_name": "Apple Inc.",
        "ticker": "AAPL",
        "fiscal_year": "2025",
        "executive_summary": "Apple Inc. faces a pivotal year focused on integrating Generative AI across its ecosystem while managing regulatory headwinds in the EU and US. Revenue stability relies heavily on iPhone cycles, but Services growth remains the primary margin driver. Supply chain diversification away from China is accelerating but presents short-term operational risks.",
        "outlook": "The company is positioning for a 'Super Cycle' driven by AI-enabled hardware. Strategic investments suggest a shift from pure hardware to a hybrid services-hardware dependency. We maintain a BULLISH outlook with moderate volatility due to antitrust litigation.",
        "key_risks": [
            {
                "severity": "High",
                "risk": "Antitrust & Regulatory Pressure",
                "description": "DOJ lawsuit in the US and Digital Markets Act (DMA) in the EU threaten the App Store commission model and ecosystem exclusivity."
            },
            {
                "severity": "Medium",
                "risk": "China Supply Chain Dependency",
                "description": "Geopolitical tensions and local competition (Huawei) pose risks to both manufacturing throughput and regional market share."
            },
            {
                "severity": "Low",
                "risk": "Innovation Pace",
                "description": "Slower iteration on hardware form factors compared to foldable competitors may impact perceived brand leadership."
            }
        ]
    }
    
    return templates.TemplateResponse(
        "financial_report.html", 
        {"request": request, "data": mock_data}
    )

@app.get("/agent/state/{thread_id}", tags=["Agent Control"])
async def get_agent_state(thread_id: str, session: AsyncSession = Depends(get_session)):
    """
    Get the current state of a conversation thread.
    Checks if the agent is paused or has errors.
    """
    titan = TitanGraph(session)
    agent = await titan.get()
    config = {"configurable": {"thread_id": thread_id}}

    current_state = await agent.aget_state(config)

    if not current_state.values:
        return {"status": "Empty/New Thread"}

    state_data = current_state.values

    return {
        "next_step": state_data.get("next_step"),
        "error_message": state_data.get("error_message"),
        "hystory_steps": state_data.get("loop_step"),
        "last_node": current_state.next
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)