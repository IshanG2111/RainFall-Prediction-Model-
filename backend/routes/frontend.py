from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Templates directory is at project root/templates
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def serve_index(request: Request):
    index_path = _TEMPLATES_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("Frontend template not found.", status_code=404)
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"), status_code=200)
