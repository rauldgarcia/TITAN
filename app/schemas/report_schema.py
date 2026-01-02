from pydantic import BaseModel, Field
from typing import List

class RiskItem(BaseModel):
    risk: str = Field(description="Name of the risk factor")
    severity: str = Field(description="High, Medium, or Low")
    description: str = Field(description="Brief explanation of the risk")

class FinancialSummary(BaseModel):
    company_name: str
    ticker: str
    fiscal_year: str
    executive_summary: str = Field(description="A strategic overview of the company's status")
    key_risks: List[RiskItem]
    outlook: str = Field(description="Future outlook or strategic goals mentioned")