import logging
from typing import Dict, List, Optional

from openai import AsyncOpenAI

from ..config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Wrapper around OpenAI to provide contextual mission-aligned answers."""

    def __init__(self) -> None:
        api_key = settings.openai_api_key
        self._client: Optional[AsyncOpenAI] = AsyncOpenAI(api_key=api_key) if api_key else None

    async def ask(
        self,
        question: str,
        *,
        history: Optional[List[Dict[str, str]]] = None,
        context: Optional[str] = None,
    ) -> str:
        question = (question or "").strip()
        if not question:
            raise ValueError("Question cannot be empty")

        if self._client is None:
            raise RuntimeError("OpenAI API key is not configured")

        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are ImpactView's mission-aligned insights assistant. "
                    "Respond with concise, actionable guidance for social impact professionals. "
                    "Favor clear next steps, cite relevant metrics when provided, and maintain an encouraging tone."
                ),
            }
        ]

        if context:
            messages.append({"role": "system", "content": f"Additional context:\n{context}"})

        for item in history or []:
            role = item.get("role")
            content = (item.get("content") or "").strip()
            if not content:
                continue
            if role == "ai":
                messages.append({"role": "assistant", "content": content})
            else:
                messages.append({"role": "user", "content": content})

        messages.append({"role": "user", "content": question})

        try:
            completion = await self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.2,
                max_tokens=450,
            )
        except Exception as exc:  # pragma: no cover - network / OpenAI failures
            logger.exception("AI completion failed: %%s", exc)
            raise RuntimeError("Failed to query AI service") from exc

        choice = completion.choices[0] if completion.choices else None
        if not choice or not choice.message or not choice.message.content:
            raise RuntimeError("AI service returned an empty response")

        return choice.message.content.strip()
