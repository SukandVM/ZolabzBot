# app/services/llm_service.py

import httpx
import requests
from typing import Dict, Any
from app.core.config import settings


# -------------------------
# Ollama Provider
# -------------------------
class OllamaProvider:
    def __init__(self):
        self.model = settings.LLM_MODEL
        self.base_url = settings.LLM_BASE_URL

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
            )

        if response.status_code != 200:
            raise RuntimeError(f"Ollama error: {response.text}")

        data = response.json()
        return data.get("response", "").strip()


# -------------------------
# llama.cpp Provider
# -------------------------
class LlamaCppProvider:
    def __init__(self):
        self.base_url = settings.LLM_BASE_URL  # http://localhost:8001

    async def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/completion",
            json={
                "prompt": prompt,
                "n_predict": 128,
                "temperature": 0.7,
            },
            timeout=120,
        )

        if response.status_code != 200:
            raise RuntimeError(f"llama.cpp error: {response.text}")

        return response.json().get("content", "").strip()


# -------------------------
# Provider selector
# -------------------------
def get_provider():
    if settings.LLM_PROVIDER == "ollama":
        return OllamaProvider()
    if settings.LLM_PROVIDER == "llamacpp":
        return LlamaCppProvider()

    raise RuntimeError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")


provider = get_provider()


# -------------------------
# Public API
# -------------------------
async def generate_question(role: str, skill: str) -> str:
    prompt = (
        f"You are an AI interviewer.\n"
        f"Generate ONE technical interview question.\n"
        f"Role: {role}\n"
        f"Skill: {skill}\n"
        f"Only output the question."
    )
    return await provider.generate(prompt)


async def score_answer(question: str, answer: str) -> Dict[str, Any]:
    prompt = (
        f"Question: {question}\n"
        f"Answer: {answer}\n\n"
        f"Score from 0 to 10 and explain briefly.\n"
        f"Format:\n"
        f"SCORE: <number>\n"
        f"REASON: <text>"
    )

    raw = await provider.generate(prompt)

    score = 0.0
    reason = "N/A"

    if "SCORE:" in raw:
        try:
            score = float(raw.split("SCORE:")[1].split("\n")[0].strip())
        except Exception:
            pass

    if "REASON:" in raw:
        reason = raw.split("REASON:")[1].strip()

    return {
        "score": score,
        "explanation": reason,
        "raw": raw,
    }
