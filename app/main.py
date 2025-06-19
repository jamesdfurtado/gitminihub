from fastapi import FastAPI
from app.pages import homepage, user, repo

app = FastAPI()

app.include_router(homepage.router)
app.include_router(user.router)
app.include_router(repo.router)
