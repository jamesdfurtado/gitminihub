import httpx
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils import (
    load_users, save_users, normalize_username, is_invalid_username,
    is_invalid_password, hash_password, verify_password, get_current_user
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/cli-login", response_class=HTMLResponse)
async def cli_login_page(request: Request, cli_token: str | None = None):
    """CLI login page with option to login or signup."""
    if not cli_token:
        raise HTTPException(status_code=400, detail="Missing CLI token")
    
    user = get_current_user(request)
    return templates.TemplateResponse(request, "cli_login.html", {
        "user": user,
        "cli_token": cli_token
    })

@router.post("/cli-login")
async def cli_login(
    request: Request,
    cli_token: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    action: str = Form(...)  # "login" or "signup"
):
    """Handle CLI login or signup."""
    if not cli_token:
        raise HTTPException(status_code=400, detail="Missing CLI token")
    
    user = get_current_user(request)
    username = normalize_username(username)
    
    if is_invalid_username(username):
        return templates.TemplateResponse(request, "cli_login.html", {
            "error": "Invalid username. Use only lowercase letters, numbers, or dashes.",
            "user": user,
            "cli_token": cli_token
        })
    
    if is_invalid_password(password):
        return templates.TemplateResponse(request, "cli_login.html", {
            "error": "Password cannot contain spaces.",
            "user": user,
            "cli_token": cli_token
        })
    
    users = load_users()
    
    if action == "signup":
        # Handle signup
        if username in users:
            return templates.TemplateResponse(request, "cli_login.html", {
                "error": "Username already exists.",
                "user": user,
                "cli_token": cli_token
            })
        
        # Create new user
        users[username] = {
            "password_hash": hash_password(password),
            "repos": [],
            "api_keys": []
        }
        save_users(users)
        
        # Call the API endpoint to complete authentication
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{request.base_url}auth/verify",
                    json={
                        "cli_token": cli_token,
                        "username": username,
                        "password": password
                    }
                )
                
                if response.status_code != 200:
                    return templates.TemplateResponse(request, "cli_login.html", {
                        "error": "Authentication failed. Please try again.",
                        "user": user,
                        "cli_token": cli_token
                    })
        except Exception:
            return templates.TemplateResponse(request, "cli_login.html", {
                "error": "Authentication service unavailable. Please try again.",
                "user": user,
                "cli_token": cli_token
            })
        
        # Redirect to success page
        return RedirectResponse(f"/cli-success?cli_token={cli_token}", status_code=302)
    
    elif action == "login":
        # Handle login - verify credentials and call API endpoint
        user_data = users.get(username)
        
        if not user_data or not verify_password(password, user_data["password_hash"]):
            return templates.TemplateResponse(request, "cli_login.html", {
                "error": "Invalid username or password.",
                "user": user,
                "cli_token": cli_token
            })
        
        # Call the API endpoint to complete authentication
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{request.base_url}auth/verify",
                    json={
                        "cli_token": cli_token,
                        "username": username,
                        "password": password
                    }
                )
                
                if response.status_code != 200:
                    return templates.TemplateResponse(request, "cli_login.html", {
                        "error": "Authentication failed. Please try again.",
                        "user": user,
                        "cli_token": cli_token
                    })
        except Exception:
            return templates.TemplateResponse(request, "cli_login.html", {
                "error": "Authentication service unavailable. Please try again.",
                "user": user,
                "cli_token": cli_token
            })
        
        # Redirect to success page
        return RedirectResponse(f"/cli-success?cli_token={cli_token}", status_code=302)
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

@router.get("/cli-success", response_class=HTMLResponse)
async def cli_success_page(request: Request, cli_token: str | None = None):
    """Success page after CLI authentication."""
    if not cli_token:
        raise HTTPException(status_code=400, detail="Missing CLI token")
    
    user = get_current_user(request)
    return templates.TemplateResponse(request, "cli_success.html", {
        "user": user,
        "cli_token": cli_token
    }) 