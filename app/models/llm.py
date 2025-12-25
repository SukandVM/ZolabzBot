# app/models/llm.py
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    role: str
    skill: str


class QuestionResponse(BaseModel):
    question: str


class ScoreRequest(BaseModel):
    question: str
    answer: str


class ScoreResponse(BaseModel):
    score: float
    explanation: str
    raw: str
