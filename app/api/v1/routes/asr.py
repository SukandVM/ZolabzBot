from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile
import os

from app.services.asr_service import transcribe_audio
from app.core.logging import logger

router = APIRouter(prefix="/v1/asr", tags=["ASR"])


@router.post("/transcribe")
async def transcribe(
    candidate_id: str = Form(...),
    audio_file: UploadFile = File(...),
    question: str | None = Form(None),
):
    if not audio_file.filename.endswith((".wav", ".mp3")):
        raise HTTPException(
            status_code=400, detail="Only .wav or .mp3 files are supported"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=audio_file.filename) as tmp:
        content = await audio_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = transcribe_audio(tmp_path)

        logger.info(f"ASR transcription completed for {candidate_id}")

        return {
            "candidate_id": candidate_id,
            "transcript": result["transcript"],
            "confidence": result.get("confidence"),
        }

    finally:
        os.remove(tmp_path)
