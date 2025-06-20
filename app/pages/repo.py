from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/r")
templates = Jinja2Templates(directory="app/templates")

@router.get("/{username}/{repo_name}", response_class=HTMLResponse)
async def view_repo(request: Request, username: str, repo_name: str):
    return templates.TemplateResponse("repo.html", {
        "request": request,
        "username": username,
        "repo_name": repo_name
    })
