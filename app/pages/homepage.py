from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.pages.utils import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(request, "index.html", {"user": user})

@router.get("/search", response_class=HTMLResponse)
async def search(request: Request, user: str = "", repo: str = ""):
    if not user:
        return templates.TemplateResponse(request, "index.html", {
            "error": "User does not exist"
        })

    if repo:
        return RedirectResponse(url=f"/{user}/{repo}")
    else:
        return RedirectResponse(url=f"/{user}")
