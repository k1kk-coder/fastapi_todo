from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db_dir.db import engine, get_db
from db_dir.db_models import Base, Users
from db_dir.pydantic_models import UserVerification
from exceptions import get_user_exception, raise_item_not_found

from ..api.auth_api import get_current_user, get_password_hash, verify_password

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

Base.metadata.create_all(bind=engine)


@users_router.get("/")
async def get_all_users(db: Session = Depends(get_db)):
    return db.query(Users).all()


@users_router.get("/user/{user_id}")
async def get_user_by_path(
    user_id: int,
    db: Session = Depends(get_db)
):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is not None:
        return user_model
    raise raise_item_not_found()


@users_router.put("/user/password")
async def user_password_change(
    user_verification: UserVerification,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    user_model = db.query(Users).filter(Users.id == user['id']).first()

    if user_model is not None:
        if user_verification.username == user_model.username and \
            verify_password(
                user_verification.password, user_model.hashed_password):
            user_model.hashed_password = get_password_hash(
                    user_verification.new_password
                )
            db.add(user_model)
            db.commit()
            return "seccussful"
    return "Invalid user or request"


@users_router.delete("/user/delete_account")
async def delete_user(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    user_model = db.query(Users).filter(Users.id == user['id']).first()

    if user_model is not None:
        db.query(Users).filter(Users.id == user['id']).delete()
        db.commit()
        return {
            "status": 201,
            "message": "Your profile deleted successfully"
        }
    raise get_user_exception()
