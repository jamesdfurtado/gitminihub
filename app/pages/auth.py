from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt
import os, json, datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
users_path = "app/data/users.json"

# SIGN UP PAGE ROUTES
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
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    save_users(users)

    return RedirectResponse("/login", status_code=302)



# LOGIN PAGE ROUTES
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    users = load_users()
    user = users.get(username)

    if not user or not bcrypt.verify(password, user["password_hash"]):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password."
        })

    # Temporary: fake login "success"
    return RedirectResponse("/", status_code=302)



# LOADING AND FETCHING USERS from users.json "database"

def load_users():
    if os.path.exists(users_path):
        with open(users_path, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(users_path, "w") as f:
        json.dump(users, f, indent=2)