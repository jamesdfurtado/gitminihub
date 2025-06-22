from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.pages.utils import (
    load_users,
    normalize_username,
    is_invalid_password,
    verify_password,
)

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
    username = normalize_username(username)

    if is_invalid_password(password):
        return templates.TemplateResponse(request, "login.html", {
            "error": "Password cannot contain spaces."
        })

    users = load_users()
    user = users.get(username)

    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(request, "login.html", {
            "error": "Invalid username or password."
        })

    return RedirectResponse("/", status_code=302)
