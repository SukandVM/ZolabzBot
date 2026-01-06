from fastapi import APIRouter, HTTPException
from app.core.logging import logger

from app.services.resume_storage_service import get_resume
from app.services.interview_flow_service import (
    start_interview,
    get_next_question,
    submit_answer,
    get_interview_status,
)

from app.services.report_service import generate_interview_report

from app.models.interview_flow import (
    StartInterviewRequest,
    StartInterviewResponse,
    NextQuestionResponse,
    SubmitAnswerRequest,
    InterviewStatusResponse,
)

router = APIRouter(prefix="/v1/interview", tags=["Interview Flow"])


@router.post("/start", response_model=StartInterviewResponse)
async def start(payload: StartInterviewRequest):
    resume = get_resume(payload.candidate_id)

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found. Please upload resume before starting interview.",
        )

    skills = resume.get("skills", [])
    if not skills:
        raise HTTPException(status_code=400, detail="No skills found in resume.")

    await start_interview(payload.candidate_id, skills)

    logger.info(f"[START] candidate={payload.candidate_id}, skills={skills}")

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
    interview_state = await submit_answer(
        payload.candidate_id,
        payload.skill,
        payload.question,
        payload.answer_text,
        payload.cv_violation,
    )

    return {
        "candidate_id": payload.candidate_id,
        "status": interview_state["status"],
        "results": interview_state["results"],
    }


@router.get("/status/{candidate_id}", response_model=InterviewStatusResponse)
async def status(candidate_id: str):
    interview_state = get_interview_status(candidate_id)
    if not interview_state:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "candidate_id": candidate_id,
        "status": interview_state["status"],
        "results": interview_state["results"],
    }


@router.get("/report/{candidate_id}")
async def interview_report(candidate_id: str):
    interview_state = get_interview_status(candidate_id)

    if not interview_state:
        raise HTTPException(status_code=404, detail="Session not found")

    if interview_state["status"] != "COMPLETED":
        raise HTTPException(status_code=400, detail="Interview not completed yet")

    return generate_interview_report(candidate_id, interview_state)
