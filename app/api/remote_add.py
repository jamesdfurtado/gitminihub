from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.utils import load_users, get_repo_root
import os

router = APIRouter()

class RemoteAddRequest(BaseModel):
    user: str
    api_key: str
    repo: str

@router.post("/api/remote/add")
async def remote_add(body: RemoteAddRequest):
    username = body.user
    api_key = body.api_key
    repo_name = body.repo

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

    # Gather branch info from .gitmini/refs/heads
    heads_dir = os.path.join(user_repo_path, ".gitmini", "refs", "heads")
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
