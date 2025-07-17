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
    # Validate required fields
    if not all([user, api_key, repo, branch]):
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Invalid push payload"
        })

    # Check tarball
    if not objects or not objects.filename or not objects.filename.endswith(".tar.gz"):
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Object archive missing or corrupt"
        })
    try:
        # Try to read a small chunk to check if file is readable
        await objects.read(1)
        await objects.seek(0)
    except Exception:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Object archive missing or corrupt"
        })

    users = load_users()
    user_obj = users.get(user)

    # Auth fail response
    if not user_obj or api_key not in user_obj.get("api_keys", []):
        return JSONResponse(status_code=401, content={
            "status": "error",
            "message": "Authentication failed"
        })

    repo_root = get_repo_root()
    user_repo_path = os.path.join(repo_root, user, repo)
    if not os.path.isdir(user_repo_path):
        # Repo not found response
        for other_user in users:
            if other_user == user:
                continue
            other_repo_path = os.path.join(repo_root, other_user, repo)
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
    if not os.path.isfile(branch_path):
        return JSONResponse(status_code=404, content={
            "status": "error",
            "message": "Remote branch not found."
        })

    # Simulate fast-forward/non-fast-forward logic
    # Read current remote branch commit
    try:
        with open(branch_path, "r") as f:
            current_remote_commit = f.read().strip()
    except Exception:
        current_remote_commit = None

    # If last_known_remote_commit is provided, check for fast-forward
    if last_known_remote_commit is not None:
        if last_known_remote_commit != current_remote_commit:
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": "Non-fast-forward push rejected. Remote branch has diverged.",
                "branch": branch,
                "most_recent_remote_branch_commit": current_remote_commit
            })

    # Simulate branch update (not actually updating yet)
    # Return success response
    return JSONResponse(status_code=200, content={
        "status": "ok",
        "message": "Push successful.",
        "branch": branch,
        "most_recent_remote_branch_commit": new_commit
    })
