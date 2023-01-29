import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import (APIRouter, Depends, Form, HTTPException, Request,
                     Response, status)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db_dir.db import engine, get_db
from db_dir.db_models import Base, Users

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


templates = Jinja2Templates(directory="templates")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


auth_front_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)


class LoginForm:
    def __init__(self, request: Request) -> None:
        self.request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_auth_form(self):
        form = await self.request.form()
        self.username = form["email"]
        self.password = form["password"]


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users)\
        .filter(Users.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: str, expires_delta: Optional[timedelta] = None
):
    encode = {'sub': username, 'id': user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not Found")


@auth_front_router.get('/', response_class=HTMLResponse)
async def auth_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@auth_front_router.post('/', response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_auth_form()
        response = RedirectResponse(
            url='/todos', status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(
            response=response,
            form_data=form,
            db=db
        )
        if not validate_user_cookie:
            msg = "Incorrect username or password"
            return templates.TemplateResponse(
                "login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown error"
        return templates.TemplateResponse(
            "login.html", {"request": request, "msg": msg})


@auth_front_router.get('/logout')
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response


@auth_front_router.get('/register')
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@auth_front_router.post('/register', response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(),
    username: str = Form(),
    first_name: str = Form(),
    last_name: str = Form(),
    password: str = Form(),
    password2: str = Form(),
    db: Session = Depends(get_db)
):
    validation1 = db.query(Users).filter(Users.username == username).first()
    validation2 = db.query(Users).filter(Users.email == email).first()

    if password != password2:
        msg = "Passwords do not match"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg})
    if validation1 is not None:
        msg = "This username already taken"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg})
    if validation2 is not None:
        msg = "This email already taken"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg})

    user_model = Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = first_name
    user_model.last_name = last_name
    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = "Account successfully created"
    return templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg})


@auth_front_router.post('/token')
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=200)
    token = create_access_token(
        user.username, user.id, expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=True)

    return True
