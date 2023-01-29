import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

engine = create_engine(os.getenv("DB_CONFIG"), echo=True)

Session = sessionmaker(bind=engine)


def get_db():
    try:
        db = Session()
        yield db
    finally:
        db.close()
