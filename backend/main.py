from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from db_dir.db import engine
from db_dir.db_models import Base
from routers.api.address import address_router
from routers.api.auth_api import auth_router
from routers.api.todos_api import todos_router
from routers.api.users_api import users_router
from routers.fullstack.auth import auth_front_router
from routers.fullstack.todos import todos_front_router
from routers.fullstack.users import users_front_router

app = FastAPI(title="Todo app")

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

api_prefix = "/api/v1"


@app.get('/', include_in_schema=False)
async def root():
    return RedirectResponse(
        url='/todos', status_code=status.HTTP_302_FOUND)


app.include_router(auth_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(todos_router, prefix=api_prefix)
app.include_router(address_router, prefix=api_prefix)
app.include_router(todos_front_router, include_in_schema=False)
app.include_router(users_front_router, include_in_schema=False)
app.include_router(auth_front_router, include_in_schema=False)
