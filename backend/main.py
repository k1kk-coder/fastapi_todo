from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import engine, get_db
from db_models import Base, Todos
from pydantic_models import Todo
from exceptions import raise_item_not_found
from routers.auth import router, get_current_user, get_user_exception


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)


@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}")
async def read_todo(
    todo_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()
    todo = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()
    if todo is not None:
        return todo
    raise raise_item_not_found()


@app.get("/todos/user")
async def read_all_by_user(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@app.post("/")
async def create_todo(
    todo: Todo,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()
    todo_model = Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.completed = todo.completed
    todo_model.owner_id = user.get('id')

    db.add(todo_model)
    db.commit()

    return {
        "status": 201,
        'message': 'Todo created successfully'
        }


@app.put("/{todo_id}")
async def update_todo(
    todo_id: int,
    todo: Todo,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()
    todo_model = db.query(Todos)\
        .filter(Todos.owner_id == user.get("id"))\
        .filter(Todos.id == todo_id).first()

    if todo_model is not None:
        todo_model.title = todo.title
        todo_model.description = todo.description
        todo_model.priority = todo.priority
        todo_model.completed = todo.completed

        db.commit()

        return {
            "status": 200,
            'message': 'Todo updated successfully'
            }
    raise raise_item_not_found()


@app.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    todo_model = db.query(Todos)\
        .filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()

    if todo_model is not None:
        db.query(Todos).filter(Todos.id == todo_id).delete()
        db.commit()
        return {
            "status": 201,
            'message': 'Todo deleted successfully'
            }
    raise raise_item_not_found()
