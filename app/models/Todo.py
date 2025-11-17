"""Pydantic models for Todo API."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self  # ← necesario para mypy en Python < 3.11


class TodoBase(BaseModel):
    """Base Todo model."""

    completed: Optional[bool] = None
    description: Optional[str] = None


class CreateTodoDTO(TodoBase):
    """Model for creating a new Todo"""

    @model_validator(mode="after")
    def at_least_one_field(self) -> Self:
        if self.description is None and self.completed is None:
            raise ValueError("At least one field must be provided")
        return self

    @field_validator("description")
    def description_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("description cannot be empty")
        return v


class UpdateTodoDTO(TodoBase):
    """Model for updating a Todo"""

    @model_validator(mode="after")
    def at_least_one_field(self) -> Self:
        if self.description is None and self.completed is None:
            raise ValueError("At least one field must be provided")
        return self

    @field_validator("description")
    def description_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("description cannot be empty")
        return v


class Todo(TodoBase):
    """Model with all attrs including id"""

    id: int = Field(..., description="Unique identifier for the todo")
