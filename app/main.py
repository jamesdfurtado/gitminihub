from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Homepage
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Search
@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, user: str = "", repo: str = ""):
    if not user:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "User does not exist"
        })

    if repo:
        return RedirectResponse(url=f"/{user}/{repo}")
    else:
        return RedirectResponse(url=f"/{user}")

# User profile
@app.get("/{username}", response_class=HTMLResponse)
async def user_profile(request: Request, username: str):
    # mock data for now
    repos = ["my-repo", "weatherapp", "cool-stuff"]
    return templates.TemplateResponse("user.html", {
        "request": request,
        "username": username,
        "repos": repos
    })

# Repositoriy
@app.get("/{username}/{repo_name}", response_class=HTMLResponse)
async def view_repo(request: Request, username: str, repo_name: str):
    return templates.TemplateResponse("repo.html", {
        "request": request,
        "username": username,
        "repo_name": repo_name
    })
