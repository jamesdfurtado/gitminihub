from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/{username}", response_class=HTMLResponse)
async def user_profile(request: Request, username: str):
    repos = ["my-repo", "weatherapp", "cool-stuff"]
    return templates.TemplateResponse("user.html", {
        "request": request,
        "username": username,
        "repos": repos
    })
