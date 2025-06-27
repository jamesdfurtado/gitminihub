import os
import shutil
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils import load_users, save_users, normalize_username, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/{username}/{repo_name}", response_class=HTMLResponse)
async def view_repo(request: Request, username: str, repo_name: str):
    current_user = get_current_user(request)
    username = normalize_username(username)
    users = load_users()

    if username not in users:
        return templates.TemplateResponse(request, "repo.html", {
            "username": username,
            "repo_name": repo_name,
            "error": "Repository does not exist",
            "user": current_user
        })

    repo_entry = next((r for r in users[username]["repos"] if r["name"] == repo_name), None)
    if not repo_entry:
        return templates.TemplateResponse(request, "repo.html", {
            "username": username,
            "repo_name": repo_name,
            "error": "Repository does not exist",
            "user": current_user
        })

    return templates.TemplateResponse(request, "repo.html", {
        "username": username,
        "repo_name": repo_entry["name"],
        "user": current_user
    })

@router.post("/{username}/{repo_name}/delete", response_class=HTMLResponse)
async def delete_repo(request: Request, username: str, repo_name: str, confirm_name: str = Form(...)):
    current_user = get_current_user(request)
    username = normalize_username(username)
    users = load_users()

    # Check that the user is logged in and matches the account that owns the repo.
    if not current_user or current_user != username:
        return templates.TemplateResponse(request, "repo.html", {
            "username": username,
            "repo_name": repo_name,
            "error": "You do not have permission to delete this repository.",
            "user": current_user
        })

    # Look for the target repo in the user's list of repos.
    user_repos = users.get(username, {}).get("repos", [])
    repo_entry = next((r for r in user_repos if r["name"] == repo_name), None)
    if not repo_entry:
        return templates.TemplateResponse(request, "repo.html", {
            "username": username,
            "repo_name": repo_name,
            "error": "Repository does not exist.",
            "user": current_user
        })

    # Ensure the confirmation input matches the repo name exactly.
    if confirm_name.strip() != repo_name:
        return templates.TemplateResponse(request, "repo.html", {
            "username": username,
            "repo_name": repo_name,
            "error": "Confirmation name does not match.",
            "user": current_user
        })

    # Delete the repo directory from the filesystem, if it exists.
    repo_path = os.path.join("repos", username, repo_name)
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    # Remove the repo entry from users.json and save changes.
    users[username]["repos"] = [r for r in user_repos if r["name"] != repo_name]
    save_users(users)

    # Redirect back to the user profile page after successful deletion.
    return RedirectResponse(f"/{username}", status_code=302)
