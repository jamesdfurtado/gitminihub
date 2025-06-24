from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.pages.utils import load_users, normalize_username

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/{username}/{repo_name}", response_class=HTMLResponse)
async def view_repo(request: Request, username: str, repo_name: str):
    username = normalize_username(username)
    users = load_users()

    if username not in users or repo_name not in users[username]["repos"]:
        return templates.TemplateResponse(request, "repo.html", {
            "username": username,
            "repo_name": repo_name,
            "error": "Repository does not exist"
        })

    return templates.TemplateResponse(request, "repo.html", {
        "username": username,
        "repo_name": repo_name
    })
