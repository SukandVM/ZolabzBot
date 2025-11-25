from fastapi import APIRouter

router = APIRouter(prefix="/v1/interview", tags=["Interview"])

@router.get("/health")
def interview_health():
    return {"status": "ok"}
