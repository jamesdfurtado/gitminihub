from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt
from app.pages.utils import load_users

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    # Strip spaces and decapitalize usernames
    username = username.replace(" ", "").lower()

    # reject passwords with spaces
    if " " in password:
        return templates.TemplateResponse(request, "login.html", {
            "error": "Password cannot contain spaces."
        })

    users = load_users()
    user = users.get(username)

    if not user or not bcrypt.verify(password, user["password_hash"]):
        return templates.TemplateResponse(request, "login.html", {
            "error": "Invalid username or password."
        })

    return RedirectResponse("/", status_code=302)
