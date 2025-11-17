"""TodoService"""

from typing import Annotated, Optional

from fastapi import Depends

from app.models.Todo import CreateTodoDTO, Todo, UpdateTodoDTO
from app.services.todo_lists import TodoListService, get_todo_list_service


class TodoService:
    def __init__(self, todo_list_service: TodoListService):
        self.todo_list_service = todo_list_service

    def all(self, todo_list_id: int) -> list[Todo]:
        """
        Gets all items from a given TodoList.

        Args:
            todo_list_id: The ID of the todo list

        Returns:
            The todo list items
        """
        todos = self.todo_list_service.get_todos(todo_list_id)
        todos_list: list[Todo] = todos or []

        if todos is None:
            raise ValueError(f"Todo list with ID:{todo_list_id} not found")

        return todos_list


    def get(self, todo_list_id: int, todo_id: int) -> Todo:
        """
        Gets one Todo from the given TodoList.

        Args:
            todo_list_id: The ID of the todo list
            todo_id: The ID of the todo
        Returns:
            Todo specified item of the specified todo list
        """
        todos = self.todo_list_service.get_todos(todo_list_id)

        todos_list: list[Todo] = todos or []

        if not todos_list:
            raise ValueError(f"Todo list with ID:{todo_list_id} not found")

        from typing import Optional
        todo: Optional[Todo] = next((t for t in todos_list if t.id == todo_id), None)

        if todo is None:
            raise ValueError(
                f"Todo with ID:{todo_id} from todo list with ID:{todo_list_id} not found"
            )

        return todo



    def create(self, todo_list_id: int, todo_payload: CreateTodoDTO) -> Todo:
        """
        Adds a todo to an existing TodoList.

        Args:
            todo_list_id: The ID of the todo list
            todo_payload: The item data

        Returns:
            The todo list with the newly created item
        """
        todo_list = self.todo_list_service.get(todo_list_id)
        if not todo_list:
            raise ValueError(f"Todo list with ID:{todo_list_id} not found")

        todos = todo_list.todos or []
        new_id = max([todo_item.id for todo_item in todos], default=0) + 1
        new_todo = Todo(id=new_id, **todo_payload.dict())
        todos.append(new_todo)
        todo_list.todos = todos
        return new_todo

    def update(self, todo_list_id: int, todo_id: int, todo_payload: UpdateTodoDTO) -> Todo:
        """
        Updates the given Todo of the given TodoList

        Args:
            todo_list_id: The ID of the todo list
            todo_id: The ID of the todo
            todo_payload: The item data

        Returns:
            The updated todo
        """
        todo_list = self.todo_list_service.get(todo_list_id)
        if not todo_list:
            raise ValueError(f"Todo list with ID:{todo_list_id} not found")

        todos = todo_list.todos or []
        for idx, todo in enumerate(todos):
            if todo.id == todo_id:
                updated_todo = Todo(id=todo_id, **todo_payload.dict())

                todos[idx] = updated_todo
                todo_list.todos = todos

                return updated_todo

        raise ValueError(f"Todo with ID:{todo_id} from todo list with ID:{todo_list_id} not found")

    def delete(self, todo_list_id: int, todo_id: int) -> bool:
        """
        Deletes the given Todo of the given TodoList

        Args:
            todo_list_id: The ID of the todo list
            todo_id: The ID of the todo

        Returns:
            True if deleted, False if not found
        """
        todo_list = self.todo_list_service.get(todo_list_id)
        if not todo_list:
            raise ValueError(f"Todo list with ID:{todo_list_id} not found")

        todos = todo_list.todos
        todos_list: list[Todo] = todos or []
        prev_len = len(todos_list)
        new_todos = [todo for todo in todos_list if todo.id != todo_id]
        todo_list.todos = new_todos
        if prev_len == len(todo_list.todos):
            raise ValueError(
                f"Todo with ID:{todo_id} from todo list with ID:{todo_list_id} not found"
            )
        return True


_todo_service: Optional[TodoService] = None


def get_todo_service(
    todo_list_service: Annotated[TodoListService, Depends(get_todo_list_service)]
) -> TodoService:
    """
    Singleton generator

    Args:
        todo_list_service: Injection for todo list service to handle todos

    Returns:
        global instance of todo service
    """
    global _todo_service
    if not _todo_service:
        _todo_service = TodoService(todo_list_service)
    return _todo_service
