import logging
import re
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from google.genai import Client
from google.genai.errors import ClientError as GenAIClientError
from sqlalchemy import delete, select, func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.core.config import settings
from app.database import get_db
from app.models.user import User
from app.models.agent_rate_limit import AgentRateLimit

from .embedder import SupabaseVectorStore, embed_text
from .prompts import get_system_prompt, get_user_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])

_client: Client | None = None

_RATE_LIMIT_WINDOW = 60
_RATE_LIMIT_MAX = 20


def _check_rate_limit(identifier: str, db: Session) -> None:
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW
    db.execute(
        delete(AgentRateLimit).where(
            AgentRateLimit.identifier == identifier,
            AgentRateLimit.timestamp <= window_start
        )
    )
    count = db.scalar(
        select(func.count(AgentRateLimit.id)).where(
            AgentRateLimit.identifier == identifier,
            AgentRateLimit.timestamp > window_start
        )
    )
    if count >= _RATE_LIMIT_MAX:
        db.commit()
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please slow down.",
        )
    db.add(AgentRateLimit(identifier=identifier, timestamp=now))
    db.commit()


def _sanitize_input(text: str) -> str:
    stripped = text.strip()
    stripped = re.sub(r"<[^>]*>", "", stripped)
    stripped = stripped.replace("<user_question>", "").replace("</user_question>", "")
    
    injection_keywords = [
        "ignore previous instructions", 
        "ignore all instructions",
        "system override", 
        "bypass rules",
        "developer mode",
        "jailbreak"
    ]
    for kw in injection_keywords:
        stripped = re.sub(re.escape(kw), "[removed directive]", stripped, flags=re.IGNORECASE)
        
    return stripped[:4000]


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
                detail="AI rate limit exceeded. Try again later.",
            )
        if exc.code in (401, 403):
            raise HTTPException(
                status_code=502,
                detail="AI authentication failed. Check API key configuration.",
            )
        raise HTTPException(status_code=502, detail="AI request failed. Please try again later.")
    except Exception as exc:
        logger.exception("Unexpected AI request error")
        raise HTTPException(status_code=502, detail="AI request failed. Please try again later.")

    return (response.text or "").strip()


@router.post("/chat")
async def chat(
    payload: dict[str, Any],
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _check_rate_limit(current_user.id, db)

    farm_data: dict[str, Any] | None = payload.get("farm_data")
    messages: list[dict[str, str]] = payload.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    # Input sanitization
    for msg in messages:
        msg["content"] = _sanitize_input(msg.get("content", ""))

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
            logger.warning("RAG knowledge search failed, continuing without context", exc_info=True)

        user_message = get_user_message(**farm_data)
        last_user_msg = messages[-1]["content"] if messages else ""
        messages = [
            {"role": "system", "content": system_prompt},
            *messages[:-1],
            {"role": "user", "content": f"{user_message}\n\nUser question:\n<user_question>\n{last_user_msg}\n</user_question>"},
        ]
    else:
        if messages and messages[-1]["role"] == "user":
            messages[-1]["content"] = f"<user_question>\n{messages[-1]['content']}\n</user_question>"
        messages = [{"role": "system", "content": system_prompt}, *messages]

    reply = await _query_gemini(messages)
    return {"reply": reply}


@router.post("/search")
async def search_knowledge(
    payload: dict[str, str],
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _check_rate_limit(current_user.id, db)

    query = payload.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    query = _sanitize_input(query)
    try:
        store = SupabaseVectorStore()
        vec = await embed_text(query)
        results = await store.search(vec, top_k=5)
        return {"results": results}
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Knowledge search is temporarily unavailable.")
