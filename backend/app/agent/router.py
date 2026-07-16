from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from google.genai import Client
from google.genai.errors import ClientError as GenAIClientError

from app.auth import get_current_user
from app.core.config import settings
from app.models.user import User

from .embedder import SupabaseVectorStore, embed_text
from .prompts import get_system_prompt, get_user_message

router = APIRouter(prefix="/agent", tags=["agent"])

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        key = settings.llm_api_key or settings.gemini_api_key
        if not key:
            raise HTTPException(status_code=503, detail="LLM API key not configured")
        _client = Client(api_key=key)
    return _client


def _llm_model() -> str:
    return settings.llm_model or settings.gemini_model or "gemini-2.5-flash"


async def _query_gemini(messages: list[dict[str, Any]]) -> str:
    client = _get_client()
    model = _llm_model()

    system_content = ""
    conversation = []
    for msg in messages:
        if msg["role"] == "system":
            system_content = msg["content"]
        else:
            role = "model" if msg["role"] == "assistant" else "user"
            conversation.append({"role": role, "parts": [{"text": msg["content"]}]})

    if not conversation:
        return ""

    try:
        if system_content:
            response = await client.aio.models.generate_content(
                model=model,
                contents=conversation,
                config={"system_instruction": system_content},
            )
        else:
            response = await client.aio.models.generate_content(
                model=model,
                contents=conversation,
            )
    except GenAIClientError as exc:
        if exc.code == 429:
            raise HTTPException(
                status_code=429,
                detail=f"AI rate limit exceeded. Try again later. Error: {exc}",
            )
        if exc.code in (401, 403):
            raise HTTPException(
                status_code=502,
                detail=f"AI authentication failed. Check API key. Error: {exc}",
            )
        raise HTTPException(status_code=502, detail=f"AI request failed: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI request failed: {exc}")

    return (response.text or "").strip()


@router.post("/chat")
async def chat(
    payload: dict[str, Any],
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    farm_data: dict[str, Any] | None = payload.get("farm_data")
    messages: list[dict[str, str]] = payload.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    system_prompt = get_system_prompt()

    if farm_data:
        try:
            store = SupabaseVectorStore()
            query_text = (
                f"{farm_data.get('crop_name', '')} "
                f"{farm_data.get('location', '')} "
                f"{farm_data.get('risk_level', '')}"
            )
            query_vec = await embed_text(query_text)
            results = await store.search(query_vec, top_k=3)
            if results:
                context = "\n\n".join(r["content"] for r in results)
                system_prompt += f"\n\nRelevant knowledge:\n{context}"
        except Exception:
            pass

        user_message = get_user_message(**farm_data)
        last_user_msg = messages[-1]["content"] if messages else ""
        messages = [
            {"role": "system", "content": system_prompt},
            *messages[:-1],
            {"role": "user", "content": f"{user_message}\n\nUser question: {last_user_msg}"},
        ]
    else:
        messages = [{"role": "system", "content": system_prompt}, *messages]

    reply = await _query_gemini(messages)
    return {"reply": reply}


@router.post("/search")
async def search_knowledge(
    payload: dict[str, str],
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    query = payload.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    try:
        store = SupabaseVectorStore()
        vec = await embed_text(query)
        results = await store.search(vec, top_k=5)
        return {"results": results}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
