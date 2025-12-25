from pydantic import BaseModel
from typing import List, Optional


class StartInterviewRequest(BaseModel):
    candidate_id: str
    skills: List[str]


class QuestionResponse(BaseModel):
    skill: str
    question: str


class SubmitAnswerRequest(BaseModel):
    candidate_id: str
    skill: str
    question: str
    answer_text: str
    cv_violation: bool = False


class InterviewStatusResponse(BaseModel):
    candidate_id: str
    status: str
    results: Optional[List[dict]] = None
