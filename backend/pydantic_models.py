from typing import Optional
from pydantic import BaseModel, Field


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(
        gt=0, lt=6, description="Priority must be between 1 and 5")
    completed: bool = False
