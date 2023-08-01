import json

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from database import get_db
from fastapi_oauth2.security import OAuth2
from models import User

oauth2 = OAuth2()
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "user": request.user, "json": json})


@router.get("/auth")
def sim_auth(request: Request):
    access_token = request.auth.jwt_create({
        "id": 1,
        "identity": "demo:1",
        "image": None,
        "display_name": "John Doe",
        "email": "john.doe@auth.sim",
        "username": "JohnDoe",
        "exp": 3689609839,
    })
    response = RedirectResponse("/")
    response.set_cookie(
        "Authorization",
        value=f"Bearer {access_token}",
        max_age=request.auth.expires,
        expires=request.auth.expires,
        httponly=request.auth.http,
    )
    return response


@router.get("/user")
def user_get(request: Request, _: str = Depends(oauth2)):
    return request.user


@router.get("/users")
def users_get(request: Request, db: Session = Depends(get_db), _: str = Depends(oauth2)):
    return db.query(User).all()


@router.post("/users")
async def users_post(request: Request, db: Session = Depends(get_db), _: str = Depends(oauth2)):
    data = await request.json()
    return User(**data).save(db)