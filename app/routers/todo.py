from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.Todo import CreateTodoDTO, Todo, UpdateTodoDTO
from app.services.todo import TodoService, get_todo_service

router = APIRouter(prefix="/api/todolists/{todo_list_id}/todos", tags=["todos"])


@router.get("", response_model=list[Todo], status_code=status.HTTP_200_OK)
async def index(
    todo_list_id: int, service: Annotated[TodoService, Depends(get_todo_service)]
) -> list[Todo]:
    """
    Get all todos from a specified todo list by ID.

    Args:
        todo_list_id: The ID of the todo list that owns these items.
        service: Injected TodoService instance

    Returns:
        HTTP status 200 with a list of todos

    Raises:
        HTTPException: 404 if todo list not found
    """
    try:
        return service.all(todo_list_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.get("/{todo_id}", response_model=Todo, status_code=status.HTTP_200_OK)
async def show(
    todo_list_id: int, todo_id: int, service: Annotated[TodoService, Depends(get_todo_service)]
) -> Todo:
    """
    Get one todo from the specified todo list

    Args:
        todo_list_id: The ID of the todo list that owns these items.
        todo_id: The ID of the todo to retrieve
        service: Injected TodoService instance

    Returns:
        HTTP status 200 with a single todo

    Raises:
        HTTPException: 404 if todo list not found
        HTTPException: 404 if todo not found
    """
    try:
        todo = service.get(todo_list_id, todo_id)

        if todo is None:
            raise HTTPException(
                status_code=404,
                detail=f"Todo list with ID:{todo_list_id} or todo with ID:{todo_id}  not found",
            )

        return todo

    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create(
    todo_list_id: int,
    todo_payload: CreateTodoDTO,
    service: Annotated[TodoService, Depends(get_todo_service)],
) -> Todo:
    """
    Creates one todo for the given todo list

    Args:
        todo_list_id: The ID of the todo list which should have the new item.
        todo_payload: The data of the todo to be created
        service: Injected TodoService instance

    Returns:
        HTTP status 201 with the newly created todo

    Raises:
        HTTPException: 404 if todo list not found
    """
    try:
        return service.create(todo_list_id, todo_payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.put("/{todo_id}", response_model=Todo, status_code=status.HTTP_200_OK)
async def update(
    todo_list_id: int,
    todo_id: int,
    todo_payload: UpdateTodoDTO,
    service: Annotated[TodoService, Depends(get_todo_service)],
) -> Todo:
    """
    Updates one todo for the given todo list

    Args:
        todo_list_id: The ID of the todo list which has the todo to be updated.
        todo_id: The ID of the todo to be updated
        todo_payload: The data of the todo to be updated
        service: Injected TodoService instance

    Returns:
        HTTP status 200 with the updated todo

    Raises:
        HTTPException: 404 if todo list not found
        HTTPException: 404 if todo not found
    """
    try:
        updated = service.update(todo_list_id, todo_id, todo_payload)

        if not updated:
            raise ValueError(
                f"Todo list with ID:{todo_list_id} or todo with ID:{todo_id} not found"
            )

        return updated

    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    todo_list_id: int,
    todo_id: int,
    service: Annotated[TodoService, Depends(get_todo_service)],
):
    """
    Deletes one todo for the given todo list

    Args:
        todo_list_id: The ID of the todo list which has the todo to be deleted.
        todo_id: The ID of the todo to be deleted
        service: Injected TodoService instance

    Returns:
        HTTP status 204 with no response data

    Raises:
        HTTPException: 404 if todo list not found
        HTTPException: 404 if todo not found
    """
    try:
        deleted = service.delete(todo_list_id, todo_id)

        if not deleted:
            raise ValueError("todo not found")

    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
