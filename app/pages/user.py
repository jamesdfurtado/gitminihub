from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/{username}", response_class=HTMLResponse)
async def user_profile(request: Request, username: str):

    repos = ["my-repo", "weatherapp", "cool-stuff"]
    return templates.TemplateResponse(request, "user.html", {
        "username": username,
        "repos": repos
    })
