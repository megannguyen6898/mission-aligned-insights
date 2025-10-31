from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Dataset
from ...schemas.mvp import DatasetResponse

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: uuid.UUID, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DATASET_NOT_FOUND", "message": "Dataset not found."},
        )
    return DatasetResponse(
        schema=dataset.schema or [],
        preview=dataset.preview or [],
        row_count=dataset.row_count,
        table_name=dataset.table_name,
    )
