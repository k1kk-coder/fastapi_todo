# FastAPI ToDo
A handy tool for creating and tracking your todos
with the ability to edit and mark completed.

### Installation
Clone the project 
```
git clone <link>
```

Install requirements
```
pip install -r requirements.txt
```

Fill the .env file according to the template
```
DB_CONFIG=postgresql://postgres:postgres@localhost:5432/todo
SECRET_KEY=<your 32 digits secret key>
```

Run the command
```
uvicorn main:app --reload
```
