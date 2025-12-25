from fastapi import APIRouter, HTTPException

from app.models.interview_flow import (
    StartInterviewRequest,
    StartInterviewResponse,
    NextQuestionResponse,
    SubmitAnswerRequest,
    InterviewStatusResponse,
)

from app.services.interview_flow_service import (
    start_interview,
    get_next_question,
    submit_answer,
    get_interview_status,
)

router = APIRouter(prefix="/v1/interview", tags=["Interview Flow"])


@router.post("/start", response_model=StartInterviewResponse)
async def start(payload: StartInterviewRequest):
    await start_interview(payload.candidate_id, payload.skills)
    return {
        "message": "Interview started",
        "candidate_id": payload.candidate_id,
        "status": "IN_PROGRESS",
    }


@router.get("/next/{candidate_id}", response_model=NextQuestionResponse)
async def next_question(candidate_id: str):
    result = await get_next_question(candidate_id)
    if not result:
        raise HTTPException(status_code=404, detail="No more questions")
    return result


@router.post("/submit", response_model=InterviewStatusResponse)
async def submit(payload: SubmitAnswerRequest):
    session = await submit_answer(
        payload.candidate_id,
        payload.skill,
        payload.question,
        payload.answer_text,
        payload.cv_violation,
    )
    return {
        "candidate_id": payload.candidate_id,
        "status": session["status"],
        "results": session["results"],
    }


@router.get("/status/{candidate_id}", response_model=InterviewStatusResponse)
async def status(candidate_id: str):
    session = get_interview_status(candidate_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "candidate_id": candidate_id,
        "status": session["status"],
        "results": session["results"],
    }
