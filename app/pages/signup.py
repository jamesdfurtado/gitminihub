from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils import (
    load_users,
    save_users,
    normalize_username,
    is_invalid_username,
    is_invalid_password,
    hash_password,
    get_current_user,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(request, "signup.html", {"user": user})

@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = get_current_user(request)

    if is_invalid_username(username):
        return templates.TemplateResponse(request, "signup.html", {
            "error": "Invalid username. Use only lowercase letters, numbers, or dashes.",
            "user": user
        })

    if is_invalid_password(password):
        return templates.TemplateResponse(request, "signup.html", {
            "error": "Password cannot contain spaces.",
            "user": user
        })

    normalized = normalize_username(username)
    users = load_users()

    if normalized in users:
        return templates.TemplateResponse(request, "signup.html", {
            "error": "Username already exists.",
            "user": user
        })

    users[normalized] = {
        "password_hash": hash_password(password),
        "repos": [],
        "api_keys": []
    }

    save_users(users)
    return RedirectResponse("/login", status_code=302)
