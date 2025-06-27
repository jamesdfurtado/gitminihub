import os
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.utils import (
    get_current_user,
    load_users,
    save_users,
    normalize_username,
    add_repo_to_user
)

router = APIRouter()

REPO_ROOT = "repos"  # root-level folder for remote storage


@router.post("/api/create_remote_repo")
async def create_remote_repo(request: Request, repo_name: str = Form(...)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    users = load_users()
    error = add_repo_to_user(users, current_user, repo_name)
    if error:
        return RedirectResponse(f"/?error={error}", status_code=302)

    # Save updated users.json
    save_users(users)

    # Ensure /repos folder exists
    if not os.path.exists(REPO_ROOT):
        os.makedirs(REPO_ROOT)

    # Path: repos/<username>/<repo_name>/.gitmini/
    username = normalize_username(current_user)
    reponame = normalize_username(repo_name)
    repo_path = os.path.join(REPO_ROOT, username, reponame, ".gitmini")

    if os.path.exists(repo_path):
        return RedirectResponse(f"/?error=Repository already exists", status_code=302)

    # Create remote repo scaffolding
    os.makedirs(os.path.join(repo_path, "objects"), exist_ok=True)
    os.makedirs(os.path.join(repo_path, "refs", "heads"), exist_ok=True)

#   Not sure if I want to include this right now. it might be useless

#    # Create HEAD pointing to main branch
#    with open(os.path.join(repo_path, "HEAD"), "w") as f:
#        f.write("ref: refs/heads/main")

    # Create empty main branch ref
    open(os.path.join(repo_path, "refs", "heads", "main"), "w").close()

    return RedirectResponse(f"/{username}/{reponame}", status_code=302)