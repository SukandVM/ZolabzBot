from fastapi import APIRouter, HTTPException
from app.models.interview import (
    StartInterviewRequest,
    SubmitAnswerRequest,
    QuestionResponse,
    InterviewStatusResponse,
)
from app.services.interview_flow_service import (
    start_interview,
    get_next_question,
    submit_answer,
    get_interview_status,
)

router = APIRouter(prefix="/v1/interview", tags=["Interview"])


@router.post("/start")
async def start(payload: StartInterviewRequest):
    await start_interview(payload.candidate_id, payload.skills)
    return {"message": "Interview started"}


@router.get("/next/{candidate_id}", response_model=QuestionResponse)
async def next_question(candidate_id: str):
    question = await get_next_question(candidate_id)
    if not question:
        raise HTTPException(status_code=404, detail="No more questions")
    return question


@router.post("/answer")
async def answer(payload: SubmitAnswerRequest):
    return await submit_answer(**payload.dict())


@router.get("/status/{candidate_id}", response_model=InterviewStatusResponse)
async def status(candidate_id: str):
    session = get_interview_status(candidate_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return {
        "candidate_id": candidate_id,
        "status": session["status"],
        "results": session.get("results"),
    }
