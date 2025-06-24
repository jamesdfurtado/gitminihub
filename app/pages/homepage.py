from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.pages.utils import get_current_user, load_users, normalize_username

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    user = get_current_user(request)
    users = load_users()

    all_repos = []
    for username, data in users.items():
        for repo in data["repos"]:
            all_repos.append({
                "username": username,
                "name": repo["name"],
                "created_at": repo["created_at"]
            })

    all_repos.sort(key=lambda r: r["created_at"], reverse=True)

    return templates.TemplateResponse(request, "index.html", {
        "user": user,
        "repos": all_repos
    })

@router.get("/search", response_class=HTMLResponse)
async def search(request: Request, user: str = "", repo: str = ""):
    current_user = get_current_user(request)
    user = normalize_username(user)
    users = load_users()

    if not user:
        return templates.TemplateResponse(request, "index.html", {
            "error": "Please specify a user",
            "user": current_user
        })

    if user not in users:
        return templates.TemplateResponse(request, "index.html", {
            "error": "User does not exist",
            "user": current_user
        })

    if repo:
        if any(r["name"] == repo for r in users[user]["repos"]):
            return RedirectResponse(url=f"/{user}/{repo}")
        else:
            return templates.TemplateResponse(request, "index.html", {
                "error": "Repository does not exist",
                "user": current_user
            })

    return RedirectResponse(url=f"/{user}")
