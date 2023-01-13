from fastapi import FastAPI, Depends
from db import engine
from db_models import Base
from routers.auth import auth_router
from routers.users import users_router
from routers.todos import todos_router
from routers.address import address_router
from company.companyapis import company_router
from company.dependencies import get_token_header


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(address_router)
app.include_router(todos_router)
app.include_router(
    company_router,
    prefix="/companyapis",
    tags=["companyapis"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "Internal use only"}}
)
