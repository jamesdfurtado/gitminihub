from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from app.pages import homepage, user, repo, signup, login, logout
from app.api import remote_repo
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

# Frontend routers
app.include_router(signup.router)
app.include_router(login.router)
app.include_router(logout.router)
app.include_router(homepage.router)
app.include_router(repo.router)
app.include_router(user.router)

# Backend routers
app.include_router(remote_repo.router)
