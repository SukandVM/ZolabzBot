from typing import Dict, List
from app.core.logging import logger
from app.services.llm_service import generate_question, score_answer

# In-memory session store (later Redis / DB)
INTERVIEW_SESSIONS: Dict[str, Dict] = {}


async def start_interview(candidate_id: str, skills: List[str]):
    if not skills:
        raise ValueError("No skills provided for interview")

    INTERVIEW_SESSIONS[candidate_id] = {
        "current_index": 0,
        "skills": skills,
        "results": [],
        "status": "IN_PROGRESS",
    }

    logger.info(f"Starting interview for {candidate_id}, skills={skills}")


async def get_next_question(candidate_id: str):
    session = INTERVIEW_SESSIONS.get(candidate_id)

    if not session or session["status"] != "IN_PROGRESS":
        return None

    idx = session["current_index"]

    if idx >= len(session["skills"]):
        session["status"] = "COMPLETED"
        return None

    skill = session["skills"][idx]
    question = await generate_question(role="Candidate", skill=skill)

    return {"skill": skill, "question": question}


async def submit_answer(
    candidate_id: str,
    skill: str,
    question: str,
    answer_text: str,
    cv_violation: bool = False,
):
    session = INTERVIEW_SESSIONS.get(candidate_id)

    if not session:
        raise ValueError("Interview session not found")

    if cv_violation:
        session["status"] = "FLAGGED"
        return session

    score_data = await score_answer(question, answer_text)

    session["results"].append(
        {
            "skill": skill,
            "score": score_data["score"],
            "explanation": score_data["explanation"],
        }
    )

    session["current_index"] += 1
    return session


def get_interview_status(candidate_id: str):
    return INTERVIEW_SESSIONS.get(candidate_id)
