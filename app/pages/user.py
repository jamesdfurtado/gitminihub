from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

RESERVED_PATHS = {"login", "signup", "search", "favicon.ico"}

@router.get("/{username}", response_class=HTMLResponse)
async def user_profile(request: Request, username: str):
    if username in RESERVED_PATHS:
        raise HTTPException(status_code=404)

    repos = ["my-repo", "weatherapp", "cool-stuff"]
    return templates.TemplateResponse(request, "user.html", {
        "username": username,
        "repos": repos
    })
