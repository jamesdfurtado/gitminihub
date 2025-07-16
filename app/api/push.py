from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.utils import load_users, get_repo_root
import os

router = APIRouter()

class PushRequest(BaseModel):
    user: str
    api_key: str
    repo: str
    branch: str

@router.post("/api/remote/push")
async def remote_push(body: PushRequest):
    username = body.user
    api_key = body.api_key
    repo_name = body.repo
    branch = body.branch

    users = load_users()
    user = users.get(username)

    # Auth fail response
    if not user or api_key not in user.get("api_keys", []):
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
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "message": "Push successful",
        })
    else:
        return JSONResponse(status_code=404, content={
            "status": "error",
            "message": "Remote branch not found."
        })
