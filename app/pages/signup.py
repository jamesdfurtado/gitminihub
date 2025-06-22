from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.pages.utils import (
    load_users,
    save_users,
    normalize_username,
    is_invalid_username,
    is_invalid_password,
    hash_password,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html")

@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if is_invalid_username(username):
        return templates.TemplateResponse(request, "signup.html", {
            "error": "Invalid username. Use only lowercase letters, numbers, or dashes."
        })

    if is_invalid_password(password):
        return templates.TemplateResponse(request, "signup.html", {
            "error": "Password cannot contain spaces."
        })

    normalized = normalize_username(username)
    users = load_users()

    if normalized in users:
        return templates.TemplateResponse(request, "signup.html", {
            "error": "Username already exists."
        })

    users[normalized] = {
        "password_hash": hash_password(password),
        "repos": []
    }
    save_users(users)

    return RedirectResponse("/login", status_code=302)
