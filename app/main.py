from fastapi import FastAPI
from app.pages import homepage, user, repo, auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(homepage.router)
app.include_router(repo.router)
app.include_router(user.router)
