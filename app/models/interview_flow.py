from pydantic import BaseModel

# from typing import List


class StartInterviewRequest(BaseModel):
    candidate_id: str


class StartInterviewResponse(BaseModel):
    message: str
    candidate_id: str
    status: str


class NextQuestionResponse(BaseModel):
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
    results: list
