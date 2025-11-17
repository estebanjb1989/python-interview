"""Pydantic models for TodoList API."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.Todo import Todo


class TodoListBase(BaseModel):
    """Base TodoList model with common attributes."""

    name: str = Field(..., min_length=1, description="Name of the todo list")
    todos: Optional[list[Todo]] = []

class TodoListCreate(TodoListBase):
    """Model for creating a new TodoList."""

    pass


class TodoListUpdate(TodoListBase):
    """Model for updating an existing TodoList."""

    pass


class TodoList(TodoListBase):
    """TodoList model with all attributes including ID."""

    id: int = Field(..., description="Unique identifier for the todo list")

    model_config = ConfigDict(from_attributes=True)

class ToggleCompleteRequest(BaseModel):
    completed: bool

class ToggleCompleteAsyncResponse(BaseModel):
    status: str
    todo_list_id: int
