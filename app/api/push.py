from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import JSONResponse
from app.utils import load_users, get_repo_root
import os
from typing import Optional

router = APIRouter()

@router.post("/api/remote/push")
async def remote_push(
    user: str = Form(...),
    api_key: str = Form(...),
    repo: str = Form(...),
    branch: str = Form(...),
    last_known_remote_commit: Optional[str] = Form(None),
    new_commit: Optional[str] = Form(None),
    objects: UploadFile = File(...)
):
    # Access form fields directly
    username = user
    repo_name = repo
    # api_key, branch, last_known_remote_commit, new_commit are all available as variables

    users = load_users()
    user_obj = users.get(username)

    # Auth fail response
    if not user_obj or api_key not in user_obj.get("api_keys", []):
        return JSONResponse(status_code=401, content={
            "status": "error",
            "message": "Authentication failed"
        })

    repo_root = get_repo_root()
    user_repo_path = os.path.join(repo_root, username, repo_name)
    if not os.path.isdir(user_repo_path):
        # Repo not found response
        for other_user in users:
            if other_user == username:
                continue
            other_repo_path = os.path.join(repo_root, other_user, repo_name)
            if os.path.isdir(other_repo_path):
                return JSONResponse(status_code=403, content={
                    "status": "error",
                    "message": "Repository not found or access denied"
                })
        return JSONResponse(status_code=404, content={
            "status": "error",
            "message": "Repository not found or access denied"
        })

    # Check if branch exists
    heads_dir = os.path.join(user_repo_path, ".gitmini", "refs", "heads")
    branch_path = os.path.join(heads_dir, branch)
    if os.path.isfile(branch_path):
        # Example: how to access the uploaded tarball
        # contents = await objects.read()  # Don't read if you want to stream/save to disk
        # filename = objects.filename
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "message": "Push successful",
        })
    else:
        return JSONResponse(status_code=404, content={
            "status": "error",
            "message": "Remote branch not found."
        })
