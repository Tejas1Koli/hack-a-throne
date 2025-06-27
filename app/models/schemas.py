from pydantic import BaseModel, Field
from typing import List, Optional

class ClauseAnalysisBase(BaseModel):
    clause: str
    risk_score: float = Field(..., ge=0, le=5)
    explanation: str
    clause_type: str
    safer_version: str

class DocumentAnalysis(BaseModel):
    clauses: List[ClauseAnalysisBase]
    overall_risk: float = Field(..., ge=0, le=5)

class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "Error message"},
        }
