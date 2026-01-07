from fastapi import APIRouter, UploadFile, File, Form
import tempfile
import os

from app.services.cv_service import analyze_frame
from app.core.logging import logger

router = APIRouter(prefix="/v1/cv", tags=["Computer Vision"])


@router.post("/analyze")
async def analyze(candidate_id: str = Form(...), frame: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=frame.filename) as tmp:
        content = await frame.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = analyze_frame(tmp_path)

        logger.info(f"CV analysis for {candidate_id}: {result}")

        return {"candidate_id": candidate_id, **result}

    finally:
        os.remove(tmp_path)
