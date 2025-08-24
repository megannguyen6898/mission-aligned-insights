from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path
import hashlib

router = APIRouter(prefix="/public", tags=["public"])

TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "assets" / "templates" / "universal_template.xlsx"


def _compute_etag(path: Path) -> str:
    hash_obj = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


ETAG = _compute_etag(TEMPLATE_PATH)


@router.get("/template")
async def get_universal_template():
    headers = {
        "ETag": ETAG,
        "Cache-Control": "public, max-age=86400",
    }
    return FileResponse(
        TEMPLATE_PATH,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="universal_template.xlsx",
        headers=headers,
    )
