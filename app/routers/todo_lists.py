"""TodoList API router with CRUD endpoints."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.models import TodoList, TodoListCreate, TodoListUpdate
from app.services.todo_lists import TodoListService, get_todo_list_service

router = APIRouter(prefix="/api/todolists", tags=["todolists"])


@router.get("", response_model=List[TodoList], status_code=status.HTTP_200_OK)
async def index(
    service: Annotated[TodoListService, Depends(get_todo_list_service)],
) -> List[TodoList]:
    """
    Get all todo lists.

    Returns:
        List of all TodoList objects
    """
    return service.all()


@router.get("/{todo_list_id}", response_model=TodoList, status_code=status.HTTP_200_OK)
async def show(
    todo_list_id: int,
    service: Annotated[TodoListService, Depends(get_todo_list_service)],
) -> TodoList:
    """
    Get a specific todo list by ID.

    Args:
        todo_list_id: The ID of the todo list to retrieve
        service: Injected TodoListService instance

    Returns:
        TodoList object

    Raises:
        HTTPException: 404 if todo list not found
    """
    todo_list = service.get(todo_list_id)
    if todo_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TodoList with id {todo_list_id} not found",
        )
    return todo_list


@router.post("", response_model=TodoList, status_code=status.HTTP_201_CREATED)
async def create(
    todo_list_data: TodoListCreate,
    service: Annotated[TodoListService, Depends(get_todo_list_service)],
) -> TodoList:
    """
    Create a new todo list.

    Args:
        todo_list_data: Data for creating the todo list
        service: Injected TodoListService instance

    Returns:
        The newly created TodoList object
    """
    return service.create(todo_list_data)


@router.put("/{todo_list_id}", response_model=TodoList, status_code=status.HTTP_200_OK)
async def update(
    todo_list_id: int,
    todo_list_data: TodoListUpdate,
    service: Annotated[TodoListService, Depends(get_todo_list_service)],
) -> TodoList:
    """
    Update an existing todo list.

    Args:
        todo_list_id: The ID of the todo list to update
        todo_list_data: New data for the todo list
        service: Injected TodoListService instance

    Returns:
        Updated TodoList object

    Raises:
        HTTPException: 404 if todo list not found
    """
    updated_todo_list = service.update(todo_list_id, todo_list_data)
    if updated_todo_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TodoList with id {todo_list_id} not found",
        )
    return updated_todo_list


@router.delete("/{todo_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    todo_list_id: int,
    service: Annotated[TodoListService, Depends(get_todo_list_service)],
) -> None:
    """
    Delete a todo list by ID.

    Args:
        todo_list_id: The ID of the todo list to delete
        service: Injected TodoListService instance

    Raises:
        HTTPException: 404 if todo list not found
    """
    deleted = service.delete(todo_list_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TodoList with id {todo_list_id} not found",
        )
