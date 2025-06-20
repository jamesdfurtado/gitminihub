from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt
from app.pages.utils import load_users, save_users

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    users = load_users()

    if username in users:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": "Username already exists."
        })

    users[username] = {
        "password_hash": bcrypt.hash(password),
        "repos": []
    }
    save_users(users)

    return RedirectResponse("/login", status_code=302)
