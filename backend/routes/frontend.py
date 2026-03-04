from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Templates directory is at project root/frontend/dist
_DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
@router.get("/{full_path:path}", response_class=HTMLResponse)
def serve_index(request: Request, full_path: str = ""):
    # Always serve the React index.html for unknown routes to support client-side routing
    index_path = _DIST_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("Frontend not built. Run 'npm run build' in frontend directory.", status_code=404)
    return HTMLResponse(content=index_path.read_text(), status_code=200)
