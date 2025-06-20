from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt
from app.pages.utils import load_users, save_users

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
    username = username.strip().lower()

    if not username or " " in username:
        return templates.TemplateResponse(request, "signup.html", {
            "error": "Username must be lowercase and contain no spaces."
        })

    users = load_users()

    if username in users:
        return templates.TemplateResponse(request, "signup.html", {
            "error": "Username already exists."
        })

    users[username] = {
        "password_hash": bcrypt.hash(password),
        "repos": []
    }
    save_users(users)

    return RedirectResponse("/login", status_code=302)
