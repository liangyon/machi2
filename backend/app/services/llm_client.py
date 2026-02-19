"""
LLM Provider Abstraction — swappable via LLM_PROVIDER env var.
Implementations: GroqClient, GeminiClient, OllamaClient
"""
from abc import ABC, abstractmethod
from typing import Iterator
from app.core.config import settings


class LLMClient(ABC):
    @abstractmethod
    async def complete(self, prompt: str, json_mode: bool = False) -> str: ...

    @abstractmethod
    async def stream(self, prompt: str) -> Iterator[str]: ...


class GroqClient(LLMClient):
    def __init__(self):
        import httpx
        self.client = httpx.AsyncClient(
            base_url="https://api.groq.com/openai/v1",
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
        )
        self.model = "llama-3.3-70b-versatile"

    async def complete(self, prompt: str, json_mode: bool = False) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        resp = await self.client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    async def stream(self, prompt: str) -> Iterator[str]:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }
        async with self.client.stream("POST", "/chat/completions", json=payload) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    import json
                    data = json.loads(line[6:])
                    delta = data["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta


class GeminiClient(LLMClient):
    def __init__(self):
        import httpx
        self.client = httpx.AsyncClient(
            base_url="https://generativelanguage.googleapis.com/v1beta",
        )
        self.api_key = settings.GEMINI_API_KEY
        self.model = "gemini-2.0-flash"

    async def complete(self, prompt: str, json_mode: bool = False) -> str:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = await self.client.post(
            f"/models/{self.model}:generateContent?key={self.api_key}",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    async def stream(self, prompt: str) -> Iterator[str]:
        # Gemini streaming stub — implement with streamGenerateContent
        result = await self.complete(prompt)
        yield result


class OllamaClient(LLMClient):
    def __init__(self):
        import httpx
        self.client = httpx.AsyncClient(base_url=settings.OLLAMA_BASE_URL)
        self.model = settings.OLLAMA_MODEL

    async def complete(self, prompt: str, json_mode: bool = False) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if json_mode:
            payload["format"] = "json"
        resp = await self.client.post("/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json()["response"]

    async def stream(self, prompt: str) -> Iterator[str]:
        import json
        payload = {"model": self.model, "prompt": prompt, "stream": True}
        async with self.client.stream("POST", "/api/generate", json=payload) as resp:
            async for line in resp.aiter_lines():
                if line:
                    data = json.loads(line)
                    yield data.get("response", "")
                    if data.get("done"):
                        break


def get_llm_client() -> LLMClient:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "groq":
        return GroqClient()
    elif provider == "gemini":
        return GeminiClient()
    elif provider == "ollama":
        return OllamaClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
