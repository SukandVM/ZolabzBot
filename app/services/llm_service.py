import httpx
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    pass


class OllamaProvider:
    def __init__(self):
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL

    async def generate(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()
        except Exception as e:
            logger.exception("Ollama LLM failed")
            raise LLMError(str(e))


_provider = OllamaProvider()


async def generate_question(role: str, skill: str) -> str:
    prompt = (
        f"You are an AI interviewer.\n"
        f"Generate ONE interview question for a {role} focusing on {skill}.\n"
        f"Return only the question."
    )
    return await _provider.generate(prompt)


async def score_answer(question: str, answer: str) -> Dict[str, Any]:
    prompt = (
        f"Evaluate the answer.\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n\n"
        f"Return:\nSCORE: <0-10>\nREASON: <short reason>"
    )

    raw = await _provider.generate(prompt)

    score = 0.0
    reason = "Not available"

    if "SCORE:" in raw:
        try:
            score = float(raw.split("SCORE:")[1].split("\n")[0].strip())
        except Exception:
            pass

    if "REASON:" in raw:
        reason = raw.split("REASON:")[1].strip()

    return {"score": score, "explanation": reason, "raw": raw}
