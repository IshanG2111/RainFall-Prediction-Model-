from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pathlib import Path

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
@router.get("/{full_path:path}", response_class=HTMLResponse)
def serve_index(request: Request, full_path: str = ""):
    index_path = _TEMPLATES_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("index.html not found in templates/", status_code=404)
    return HTMLResponse(content=index_path.read_text(), status_code=200)