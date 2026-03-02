from __future__ import annotations

from typing import List

import httpx


class OpenAIClient:
    """Minimal async client for OpenAI Embeddings API.

    - Uses direct HTTPS call (no extra SDK dependency)
    - Returns embedding as list[float]
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self._api_key = api_key

    async def embed(
        self,
        *,
        text: str,
        model: str,
        dimensions: int,
        timeout_seconds: int = 30,
    ) -> List[float]:
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": text,
            "model": model,
            "dimensions": dimensions,
            "encoding_format": "float",
        }

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        return data["data"][0]["embedding"]
