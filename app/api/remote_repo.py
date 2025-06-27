from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.utils import (
    get_current_user,
    load_users,
    save_users,
    normalize_username,
    add_repo_to_user,
    initialize_repo_structure,
    delete_repo_from_filesystem,
    remove_repo_from_user,
    is_repo_owner,
    get_user_repo_entry
)

router = APIRouter()

@router.post("/{username}/{repo_name}")
async def create_remote_repo(request: Request, username: str, repo_name: str):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    if normalize_username(current_user) != normalize_username(username):
        return RedirectResponse("/?error=Unauthorized", status_code=302)

    users = load_users()
    error = add_repo_to_user(users, username, repo_name)
    if error:
        return RedirectResponse(f"/?error={error}", status_code=302)

    save_users(users)

    success = initialize_repo_structure(username, repo_name)
    if not success:
        return RedirectResponse(f"/?error=Repository already exists", status_code=302)

    return RedirectResponse(f"/{username}/{repo_name}", status_code=302)


@router.post("/{username}/{repo_name}/delete")
async def delete_remote_repo(request: Request, username: str, repo_name: str, confirm_name: str = Form(...)):
    current_user = get_current_user(request)
    username = normalize_username(username)
    users = load_users()

    if not is_repo_owner(current_user, username):
        return RedirectResponse(f"/{username}/{repo_name}?error=unauthorized", status_code=302)

    repo_entry = get_user_repo_entry(users, username, repo_name)
    if not repo_entry:
        return RedirectResponse(f"/{username}/{repo_name}?error=not_found", status_code=302)

    if confirm_name.strip() != repo_name:
        return RedirectResponse(f"/{username}/{repo_name}?error=confirmation_mismatch", status_code=302)

    delete_repo_from_filesystem(username, repo_name)
    remove_repo_from_user(users, username, repo_name)
    save_users(users)

    return RedirectResponse(f"/{username}", status_code=302)
