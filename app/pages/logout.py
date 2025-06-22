from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("session")
    return response
