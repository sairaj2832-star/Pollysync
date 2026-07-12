from typing import Any

import httpx
from google.genai import Client
from google.genai.errors import ClientError as GenAIClientError, APIError as GenAIAPIError
from google.genai.types import EmbedContentConfig

from app.core.config import settings


EMBED_MODEL = "gemini-embedding-001"
DIMENSIONS = 768

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        key = settings.gemini_api_key or settings.llm_api_key
        if not key:
            raise RuntimeError(
                "No Gemini API key found. Set GEMINI_API_KEY or LLM_API_KEY in backend/.env. "
                "Get a free key at https://aistudio.google.com/apikey"
            )
        _client = Client(api_key=key)
    return _client


def _reset_client() -> None:
    global _client
    _client = None


async def embed_text(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")

    client = _get_client()
    try:
        response = await client.aio.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
            config=EmbedContentConfig(output_dimensionality=DIMENSIONS),
        )
    except GenAIClientError as exc:
        if exc.code == 401 or exc.code == 403:
            raise RuntimeError(
                f"Gemini API authentication failed (HTTP {exc.code}). "
                "Check that GEMINI_API_KEY in backend/.env is valid. "
                f"Error: {exc}"
            ) from exc
        if exc.code == 429:
            raise RuntimeError(
                "Gemini API rate limit exceeded. Wait a moment and try again. "
                f"Error: {exc}"
            ) from exc
        raise RuntimeError(f"Gemini API client error: {exc}") from exc
    except GenAIAPIError as exc:
        raise RuntimeError(f"Gemini API error: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(
            f"Failed to embed text with Gemini API. "
            f"Check network connectivity and API key validity. Error: {exc}"
        ) from exc

    if not response or not response.embeddings:
        raise RuntimeError("Gemini API returned an empty embedding response")

    embedding_obj = response.embeddings[0] if isinstance(response.embeddings, list) else response.embeddings
    values = embedding_obj.values
    if not values or len(values) != DIMENSIONS:
        raise RuntimeError(
            f"Expected {DIMENSIONS}-dimensional embedding but got "
            f"{len(values) if values else 0} dimensions"
        )

    return [float(v) for v in values]


async def embed_batch(texts: list[str]) -> list[list[float]]:
    results: list[list[float]] = []
    for text in texts:
        vec = await embed_text(text)
        results.append(vec)
    return results


def split_document(text: str, min_chars: int = 200) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    parts = text.strip().split("===")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n", 1)
        header = lines[0].strip().strip("=").strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        content = f"{header}: {body}" if header and body else (header or body)
        if len(content) < min_chars:
            if chunks:
                chunks[-1]["content"] += "\n\n" + content
            continue
        chunks.append({"header": header, "content": content})
    return chunks


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks if chunks else [text]


class SupabaseVectorStore:
    def __init__(self) -> None:
        self._url = settings.supabase_url
        self._key = settings.supabase_service_key
        if not self._url or not self._key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

    async def upsert_embeddings(self, chunks: list[dict[str, Any]]) -> None:
        async with httpx.AsyncClient(timeout=30) as client:
            rows = []
            for chunk in chunks:
                vec = chunk["embedding"]
                rows.append({
                    "content": chunk["content"],
                    "metadata": chunk.get("metadata", {}),
                    "embedding": vec,
                })
            resp = await client.post(
                f"{self._url}/rest/v1/rpc/upsert_embeddings",
                headers={
                    "apikey": self._key,
                    "Authorization": f"Bearer {self._key}",
                    "Content-Type": "application/json",
                },
                json={"rows": rows},
            )
            resp.raise_for_status()

    async def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._url}/rest/v1/rpc/match_embeddings",
                headers={
                    "apikey": self._key,
                    "Authorization": f"Bearer {self._key}",
                    "Content-Type": "application/json",
                },
                json={"query_embedding": query_embedding, "match_threshold": 0.3, "match_count": top_k},
            )
            resp.raise_for_status()
            return resp.json()

    async def ensure_table(self) -> None:
        sql = """
        CREATE TABLE IF NOT EXISTS agent_knowledge (
            id BIGSERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            metadata JSONB DEFAULT '{}',
            embedding vector(768)
        );
        CREATE INDEX IF NOT EXISTS idx_agent_knowledge_embedding
            ON agent_knowledge USING hnsw (embedding vector_cosine_ops);
        """
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._url}/rest/v1/rpc/exec_sql",
                headers={
                    "apikey": self._key,
                    "Authorization": f"Bearer {self._key}",
                    "Content-Type": "application/json",
                },
                json={"query": sql},
            )

    async def count(self) -> int:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{self._url}/rest/v1/agent_knowledge?select=count",
                headers={
                    "apikey": self._key,
                    "Authorization": f"Bearer {self._key}",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data[0]["count"] if isinstance(data, list) else 0

    async def delete_all(self) -> None:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.delete(
                f"{self._url}/rest/v1/agent_knowledge?id=gte.0",
                headers={
                    "apikey": self._key,
                    "Authorization": f"Bearer {self._key}",
                },
            )
            resp.raise_for_status()
