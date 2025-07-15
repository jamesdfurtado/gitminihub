from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils import (
    load_users,
    normalize_username,
    is_invalid_password,
    verify_password,
    create_session_cookie,
    get_current_user,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(request, "login.html", {"user": user})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = get_current_user(request)
    username = normalize_username(username)

    if is_invalid_password(password):
        return templates.TemplateResponse(request, "login.html", {
            "error": "Password cannot contain spaces.",
            "user": user
        })

    users = load_users()
    user_data = users.get(username)

    if not user_data or not verify_password(password, user_data["password_hash"]):
        return templates.TemplateResponse(request, "login.html", {
            "error": "Invalid username or password.",
            "user": user
        })

    response = RedirectResponse("/", status_code=302)
    session_cookie = create_session_cookie(username)
    response.set_cookie(key="session", value=session_cookie, httponly=True, max_age=3600)
    return response