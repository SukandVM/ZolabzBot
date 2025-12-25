from fastapi import APIRouter, HTTPException
from app.models.llm import (
    QuestionRequest,
    QuestionResponse,
    ScoreRequest,
    ScoreResponse,
)
from app.services.llm_service import generate_question, score_answer

router = APIRouter(prefix="/v1/llm", tags=["LLM"])


@router.post("/generate-question", response_model=QuestionResponse)
async def generate(payload: QuestionRequest):
    try:
        q = await generate_question(payload.role, payload.skill)
        return QuestionResponse(question=q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/score-answer", response_model=ScoreResponse)
async def score(payload: ScoreRequest):
    try:
        result = await score_answer(payload.question, payload.answer)
        return ScoreResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
