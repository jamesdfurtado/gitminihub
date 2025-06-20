from fastapi import FastAPI
from app.pages import homepage, user, repo, signup, login

app = FastAPI()

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(homepage.router)
app.include_router(repo.router)
app.include_router(user.router)
