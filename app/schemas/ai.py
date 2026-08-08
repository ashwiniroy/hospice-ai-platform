from pydantic import BaseModel
from typing import Literal


class AskRequest(BaseModel):
    question: str
    state: str | None = None
    ownership: str | None = None
    top_k: int = 5
    mode: Literal["manual", "langchain","langgraph"] = "manual"
    thread_id: str | None = None


class SourceResponse(BaseModel):
    id: str | None = None
    score: float | None = None
    organization_name: str | None = None
    doing_business_as_name: str | None = None
    city: str | None = None
    state: str | None = None
    npi: str | None = None
    ccn: str | None = None
    proprietary_nonprofit: str | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceResponse]