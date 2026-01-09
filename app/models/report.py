from typing import Optional
from sqlmodel import SQLModel, Field
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from datetime import datetime


class FinancialReport(SQLModel, table=True):
    __tablename__ = "financial_reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    company_ticker: str = Field(index=True)
    year: int
    report_type: str = Field(default="10-K")
    section: str
    content: str

    embedding: list[float] = Field(sa_column=Column(Vector(768)))

    created_at: datetime = Field(default_factory=datetime.utcnow)
