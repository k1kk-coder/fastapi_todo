from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db_dir.db import engine, get_db
from db_dir.db_models import Base, Users

from .auth import get_current_user, get_password_hash, verify_password

users_front_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


@users_front_router.get("/edit-password", response_class=HTMLResponse)
async def edit_password_form(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(
            url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "edit-user-password.html", {"request": request})


@users_front_router.post("/edit-password", response_class=HTMLResponse)
async def edit_password(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    password2: str = Form(),
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(
            url="/auth", status_code=status.HTTP_302_FOUND)

    if password == password2:
        return templates.TemplateResponse(
            "edit-user-password.html",
            {"request": request, "msg": "Passwords should not match"}
        )

    msg = "Wrong username or password"

    user_data = db.query(Users).filter(Users.username == username).first()
    if user_data is not None:
        if username == user_data.username and verify_password(
            password, user_data.hashed_password
        ):
            user_data.hashed_password = get_password_hash(password2)
            db.add(user_data)
            db.commit()
            msg = "Password updated successfully!"

    return templates.TemplateResponse(
        "edit-user-password.html", {
            "request": request, "user": user, "msg": msg})
