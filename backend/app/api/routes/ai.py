import logging
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...api.deps import get_current_user
from ...models.user import User
from ...services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])
_ai_service = AIService()


class ChatMessage(BaseModel):
    role: Literal["user", "ai"]
    content: str = Field(..., min_length=1)


class AskAIRequest(BaseModel):
    question: str = Field(..., min_length=1)
    history: List[ChatMessage] = Field(default_factory=list)
    context: Optional[str] = None


class AskAIResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=AskAIResponse)
async def ask_ai(
    payload: AskAIRequest,
    current_user: User = Depends(get_current_user),
) -> AskAIResponse:
    try:
        answer = await _ai_service.ask(
            payload.question,
            history=[message.model_dump() for message in payload.history],
            context=payload.context,
        )
        return AskAIResponse(answer=answer)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - unexpected failures
        logger.exception("AI request failed for user %s: %s", current_user.id, exc)
        raise HTTPException(status_code=500, detail="Failed to process AI request") from exc
