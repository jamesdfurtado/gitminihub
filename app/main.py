from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from app.pages import homepage, user, repo, signup, login, logout, cli_login
from app.api import remote_repo, cli_auth, remote_add, push
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Prevent caching globally
@app.middleware("http")
async def disable_caching(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response

# Backend routes
app.include_router(cli_auth.router)
app.include_router(remote_repo.router)
app.include_router(remote_add.router)
app.include_router(push.router)

# Frontend routes
app.include_router(signup.router)
app.include_router(login.router)
app.include_router(logout.router)
app.include_router(homepage.router)
app.include_router(cli_login.router)
app.include_router(repo.router)
app.include_router(user.router)
