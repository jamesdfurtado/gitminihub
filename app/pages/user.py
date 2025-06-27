from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils import (
    load_users,
    normalize_username,
    get_current_user
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/{username}", response_class=HTMLResponse)
async def user_profile(request: Request, username: str):
    current_user = get_current_user(request)
    username = normalize_username(username)
    users = load_users()

    if username not in users:
        return templates.TemplateResponse(request, "user.html", {
            "error": "User does not exist",
            "username": username,
            "repos": [],
            "user": current_user
        })

    repos = sorted(users[username]["repos"], key=lambda r: r["created_at"], reverse=True)
    return templates.TemplateResponse(request, "user.html", {
        "username": username,
        "repos": repos,
        "user": current_user
    })
