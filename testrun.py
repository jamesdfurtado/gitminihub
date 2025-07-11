import os
import uvicorn

# Set test environment variables
os.environ["GITMINIHUB_USERS_PATH"] = "tests/data/users.json"
os.environ["GITMINIHUB_REPO_ROOT"] = "tests/data/repos/"
os.environ["GITMINIHUB_SECRET"] = "testsecret"

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 