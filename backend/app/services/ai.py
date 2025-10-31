from __future__ import annotations

import json
import time
from typing import Dict, List, Optional

import httpx

from ..config import settings
from ..models import Dataset
from .dashboards import load_dataset_frame  # reuse data loader


class AIServiceError(Exception):
    """Raised when the AI provider is unavailable or returns an error."""


def _build_context(dataset: Dataset) -> str:
    fragments: List[str] = []

    if dataset.schema:
        schema_lines = [
            f"- {col['name']} ({col.get('semantic_type', col.get('dtype'))})"
            for col in dataset.schema
        ]
        fragments.append("Columns:\n" + "\n".join(schema_lines))

    df = load_dataset_frame(dataset, limit=2000)
    if not df.empty:
        fragments.append(f"Row count: {len(df)}")
        numeric_cols = [col for col in df.select_dtypes(include=["number"]).columns]
        if numeric_cols:
            summary = df[numeric_cols].describe().loc[["mean", "sum"]]
            fragments.append("Numeric summary:\n" + summary.to_string())

    return "\n\n".join(fragments)


def ask_ai(dataset: Dataset, question: str, timeout: int = 12) -> Dict[str, object]:
    if settings.use_local_model:
        endpoint = settings.ollama_endpoint or "http://ollama:11434"
        url = f"{endpoint.rstrip('/')}/api/chat"
        system_prompt = (
            "You are a concise analytics copilot. Respond with at most three bullet points. "
            "Use the provided dataset summary to ground your answer. "
            "If the question cannot be answered from the summary, say so briefly."
        )
        context = _build_context(dataset)
        payload = {
            "model": settings.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Dataset summary:\n{context}\n\nQuestion: {question}"},
            ],
            "stream": False,
        }

        start = time.monotonic()
        try:
            response = httpx.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise AIServiceError(f"Ollama request failed: {exc}") from exc
        latency_ms = int((time.monotonic() - start) * 1000)

        data = response.json()
        message = data.get("message") or {}
        content = message.get("content")
        if not content:
            raise AIServiceError("Ollama returned an empty response")
        return {"answer": content.strip(), "usage_ms": latency_ms}

    # Fallback stub for optional OpenAI integration
    raise AIServiceError("AI_UNAVAILABLE: No AI provider is configured")
