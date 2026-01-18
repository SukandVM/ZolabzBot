import httpx
from typing import Dict, Any
from app.core.config import settings


# =====================================================
# Base Provider
# =====================================================
class BaseLLMProvider:
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError


# =====================================================
# Ollama Provider
# =====================================================
class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.model = settings.LLM_MODEL
        self.base_url = settings.LLM_BASE_URL

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{self.base_url}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
            )

        if r.status_code != 200:
            raise RuntimeError(r.text)

        return r.json().get("response", "").strip()


# =====================================================
# llama.cpp Provider
# =====================================================
class LlamaCppProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = settings.LLM_BASE_URL

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{self.base_url}/completion",
                json={
                    "prompt": prompt,
                    "n_predict": 256,
                    "temperature": 0.7,
                },
            )

        if r.status_code != 200:
            raise RuntimeError(r.text)

        return r.json().get("content", "").strip()


# =====================================================
# Groq Provider (OPENAI COMPATIBLE)
# =====================================================
class GroqProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional technical interviewer AI.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.6,
            "max_tokens": 300,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
            )

        if r.status_code != 200:
            raise RuntimeError(f"Groq error {r.status_code}: {r.text}")

        data = r.json()
        return data["choices"][0]["message"]["content"].strip()


# =====================================================
# Provider Factory
# =====================================================
def get_provider() -> BaseLLMProvider:
    p = settings.LLM_PROVIDER.lower()

    if p == "ollama":
        return OllamaProvider()

    if p == "llamacpp":
        return LlamaCppProvider()

    if p == "huggingface":
        raise RuntimeError(
            "Hugging Face free inference no longer supported. " "Use Groq or Ollama."
        )

    if p == "groq":
        return GroqProvider()

    raise RuntimeError(f"Unsupported LLM provider: {p}")


provider = get_provider()


# =====================================================
# Public API
# =====================================================
async def generate_question(role: str, skill: str) -> str:
    prompt = (
        "Generate exactly ONE technical interview question.\n"
        f"Role: {role}\n"
        f"Skill: {skill}\n"
        "Only output the question."
    )
    return await provider.generate(prompt)


async def score_answer(question: str, answer: str) -> Dict[str, Any]:
    prompt = (
        f"Question: {question}\n"
        f"Answer: {answer}\n\n"
        "Score from 0 to 10.\n"
        "Format strictly:\n"
        "SCORE: <number>\n"
        "REASON: <short explanation>"
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
