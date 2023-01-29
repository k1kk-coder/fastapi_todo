import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db_dir.db import engine, get_db
from db_dir.db_models import Base, Users
from db_dir.pydantic_models import CreateUser
from exceptions import get_user_exception, token_exception

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)


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
    encode.update({'exp': expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username": username, "id": user_id}
    except JWTError:
        raise get_user_exception()


@auth_router.post('/create_user')
async def create_user(user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = Users()
    create_user_model.username = user.username
    create_user_model.email = user.email
    create_user_model.first_name = user.first_name
    create_user_model.last_name = user.last_name
    create_user_model.hashed_password = get_password_hash(user.password)
    create_user_model.is_active = True
    create_user_model.phone_number = user.phone_number

    db.add(create_user_model)
    db.commit()


@auth_router.post('/token')
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise token_exception()
    token_expires = timedelta(minutes=200)
    token = create_access_token(
        user.username, user.id, expires_delta=token_expires)
    return {"Your token": token}
