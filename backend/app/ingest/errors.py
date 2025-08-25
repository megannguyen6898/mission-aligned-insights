from fastapi import HTTPException


class SchemaValidationError(HTTPException):
    """Raised when an uploaded file fails schema validation."""

    def __init__(self, sheet: str, missing: list[str]) -> None:
        detail = {"sheet": sheet, "missing": missing}
        super().__init__(status_code=422, detail=detail)
