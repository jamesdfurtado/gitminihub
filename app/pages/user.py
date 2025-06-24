from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.pages.utils import (
    load_users,
    save_users,
    normalize_username,
    get_current_user,
    add_repo_to_user
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

@router.post("/create_repo")
async def create_repo(request: Request, repo_name: str = Form(...)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    users = load_users()
    error = add_repo_to_user(users, current_user, repo_name)
    if error:
        return RedirectResponse(f"/{current_user}?error={error}", status_code=302)

    save_users(users)
    return RedirectResponse(f"/{current_user}/{normalize_username(repo_name)}", status_code=302)
