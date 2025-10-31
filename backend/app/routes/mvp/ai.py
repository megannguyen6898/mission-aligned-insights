from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import AIEvent, Dataset
from ...schemas.mvp import AIAskRequest, AIAskResponse
from ...services.ai import AIServiceError, ask_ai

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/ask", response_model=AIAskResponse)
def ask(body: AIAskRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == body.dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DATASET_NOT_FOUND", "message": "Dataset not found."},
        )

    try:
        result = ask_ai(dataset, body.question)
    except AIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "AI_UNAVAILABLE", "message": str(exc)},
        ) from exc

    event = AIEvent(
        workspace_id=dataset.workspace_id,
        dataset_id=dataset.id,
        question=body.question,
        answer=result["answer"],
        latency_ms=result["usage_ms"],
    )
    db.add(event)
    db.commit()

    return AIAskResponse(answer=result["answer"], usage_ms=result["usage_ms"])
