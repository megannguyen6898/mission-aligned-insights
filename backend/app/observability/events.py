import logging
from typing import Any, Optional

logger = logging.getLogger("observability")


def log_event(
    event: str,
    org_id: Optional[str] = None,
    project_id: Optional[str] = None,
    **payload: Any,
) -> None:
    """Log an observability event with context."""
    context = {"org": org_id, "project": project_id, **payload}
    logger.info("%s %s", event, context)
