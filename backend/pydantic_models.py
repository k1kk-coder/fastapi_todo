from typing import Optional
from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    phone_number: Optional[str]
    first_name: str
    last_name: str
    password: str


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(
        gt=0, lt=6, description="Priority must be between 1 and 5")
    completed: bool = False


class Address_pydantic(BaseModel):
    address1: str
    address2: Optional[str]
    city: str
    state: Optional[str]
    country: str
    postalcode: str
    apt_num: Optional[str]
