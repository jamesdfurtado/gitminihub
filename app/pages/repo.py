from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.pages.utils import load_users, normalize_username, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/{username}/{repo_name}", response_class=HTMLResponse)
async def view_repo(request: Request, username: str, repo_name: str):
    current_user = get_current_user(request)
    username = normalize_username(username)
    users = load_users()

    if username not in users or repo_name not in users[username]["repos"]:
        return templates.TemplateResponse(request, "repo.html", {
            "username": username,
            "repo_name": repo_name,
            "error": "Repository does not exist",
            "user": current_user
        })

    return templates.TemplateResponse(request, "repo.html", {
        "username": username,
        "repo_name": repo_name,
        "user": current_user
    })
