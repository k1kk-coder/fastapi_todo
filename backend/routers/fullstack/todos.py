from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db_dir.db import engine, get_db
from db_dir.db_models import Base, Todos

from .auth import get_current_user

todos_front_router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


@todos_front_router.get("/", response_class=HTMLResponse)
async def read_all(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(
            url="/auth", status_code=status.HTTP_302_FOUND)
    todos = db.query(Todos).filter(Todos.owner_id == user['id']).all()
    return templates.TemplateResponse(
        "home.html", {"request": request, "todos": todos, "user": user})


@todos_front_router.get("/add-todo", response_class=HTMLResponse)
async def add_todo_form(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(
            url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-todo.html", {"request": request})


@todos_front_router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    title: str = Form(),
    description: str = Form(),
    priority: int = Form(),
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(
            url="/auth", status_code=status.HTTP_302_FOUND)

    todo_ = Todos()
    todo_.title = title
    todo_.description = description
    todo_.priority = priority
    todo_.completed = False
    todo_.owner_id = user['id']

    db.add(todo_)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@todos_front_router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(
    request: Request, todo_id: int, db: Session = Depends(get_db)
):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(
            url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": todo, "user": user})


@todos_front_router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def update_todo(
    request: Request,
    todo_id: int,
    title: str = Form(),
    description: str = Form(),
    priority: int = Form(),
    db: Session = Depends(get_db)
):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(
            url="/auth", status_code=status.HTTP_302_FOUND)

    todo_ = db.query(Todos).filter(Todos.id == todo_id).first()

    todo_.title = title
    todo_.description = description
    todo_.priority = priority

    db.add(todo_)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@todos_front_router.get("/delete-todo/{todo_id}", response_class=HTMLResponse)
async def delete_todo(
    request: Request, todo_id: int, db: Session = Depends(get_db)
):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(
            url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user['id']).first()

    if todo_model is None:
        return RedirectResponse(
            url="/todos", status_code=status.HTTP_302_FOUND)

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@todos_front_router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(
    request: Request,
    todo_id: int,
    db: Session = Depends(get_db)
):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(
            url="/auth", status_code=status.HTTP_302_FOUND)

    todo_ = db.query(Todos).filter(Todos.id == todo_id).first()

    todo_.completed = not todo_.completed

    db.add(todo_)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
