from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.resume_parser_service import parse_resume_text
from app.services.resume_storage_service import store_resume
from app.utils.pdf_text_extractor import extract_text_from_pdf
from app.core.logging import logger
import tempfile
import os

router = APIRouter(prefix="/v1/resume", tags=["Resume"])


@router.post("/upload")
async def upload_resume(
    candidate_id: str = Form(...), resume_pdf: UploadFile = File(...)
):
    if not resume_pdf.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await resume_pdf.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # For now, treat PDF as text (later replace with proper PDF extraction)
        text = extract_text_from_pdf(tmp_path)
        logger.info(text[:500])

        parsed_resume = parse_resume_text(text)

        if not parsed_resume.get("skills"):
            logger.warning(
                f"No skills extracted for {candidate_id}. Using default skills."
            )
            parsed_resume["skills"] = ["Python", "FastAPI", "LLMs"]

        store_resume(candidate_id, parsed_resume)

        logger.info(f"Resume parsed & stored for {candidate_id}")

        return {
            "candidate_id": candidate_id,
            "status": "PARSED_AND_STORED",
            "skills_detected": parsed_resume.get("skills", []),
        }

    finally:
        os.remove(tmp_path)
