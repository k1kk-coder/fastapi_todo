from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db_dir.db import get_db
from db_dir.db_models import Address, Users
from db_dir.pydantic_models import Address_pydantic

from ..api.auth_api import get_current_user, get_user_exception

address_router = APIRouter(
    prefix="/address",
    tags=['address'],
    responses={404: {"description": "Not found"}}
)


@address_router.post("/")
async def create_address(
    address: Address_pydantic,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()
    address_model = Address()
    address_model.address1 = address.address1
    address_model.address2 = address.address2
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.postalcode = address.postalcode
    address_model.apt_num = address.apt_num

    db.add(address_model)
    db.flush()

    user_model = db.query(Users).filter(Users.id == user['id']).first()
    user_model.address_id = address_model.id

    db.add(user_model)
    db.commit()
