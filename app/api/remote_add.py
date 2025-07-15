from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.utils import load_users, get_repo_root
import os

router = APIRouter()

@router.post("/api/remote_add")
async def remote_add(request: Request):
    # Parse and validate payload
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Invalid request payload"
        })

    if not all(k in data for k in ("user", "api_key", "repo")):
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Invalid request payload"
        })

    username = data["user"]
    api_key = data["api_key"]
    repo_name = data["repo"]

    users = load_users()
    user = users.get(username)
    if not user or api_key not in user.get("api_keys", []):
        return JSONResponse(status_code=401, content={
            "status": "error",
            "message": "Authentication failed"
        })

    repo_root = get_repo_root()
    user_repo_path = os.path.join(repo_root, username, repo_name)
    if not os.path.isdir(user_repo_path):
        # Check if repo exists for another user (access denied)
        for other_user in users:
            if other_user == username:
                continue
            other_repo_path = os.path.join(repo_root, other_user, repo_name)
            if os.path.isdir(other_repo_path):
                return JSONResponse(status_code=403, content={
                    "status": "error",
                    "message": "Access denied to repository"
                })
        return JSONResponse(status_code=404, content={
            "status": "error",
            "message": "Repository not found"
        })

    # Gather branch info from refs/heads
    heads_dir = os.path.join(user_repo_path, "refs", "heads")
    branches = {}
    if os.path.isdir(heads_dir):
        for fname in os.listdir(heads_dir):
            fpath = os.path.join(heads_dir, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        commit_hash = f.read().strip()
                    branches[fname] = commit_hash
                except Exception:
                    continue

    return JSONResponse(status_code=200, content={
        "status": "ok",
        "message": "Connected to remote",
        "branches": branches
    })
