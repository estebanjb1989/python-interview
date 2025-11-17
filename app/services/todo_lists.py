"""TodoList service with in-memory storage."""

import asyncio
from typing import Optional

from app.core.event_loop import get_loop
from app.models.Todo import Todo
from app.models.TodoList import TodoList, TodoListCreate, TodoListUpdate
from app.websocket.manager import websocket_manager


class TodoListService:
    """Service for managing TodoLists with in-memory storage."""
    _locks: set[int] = set()

    def is_locked(self, list_id: int) -> bool:
        return list_id in self._locks

    def lock(self, list_id: int) -> None:
        self._locks.add(list_id)

    def unlock(self, list_id: int) -> None:
        self._locks.discard(list_id)

    def __init__(self) -> None:
        """Initialize the service with empty storage."""
        self._storage: list[TodoList] = []
        self._next_id: int = 1

    def all(self) -> list[TodoList]:
        """
        Get all todo lists.

        Returns:
            List of all TodoList objects
        """
        return self._storage.copy()

    def get(self, todo_list_id: int) -> Optional[TodoList]:
        """
        Get a specific todo list by ID.

        Args:
            todo_list_id: The ID of the todo list to retrieve

        Returns:
            TodoList object if found, None otherwise
        """
        for todo_list in self._storage:
            if todo_list.id == todo_list_id:
                return todo_list
        return None

    def create(self, todo_list_data: TodoListCreate) -> TodoList:
        """
        Create a new todo list.

        Args:
            todo_list_data: Data for creating the todo list

        Returns:
            The newly created TodoList object
        """
        new_todo_list = TodoList(id=self._next_id, name=todo_list_data.name)
        self._storage.append(new_todo_list)
        self._next_id += 1
        return new_todo_list

    def update(self, todo_list_id: int, todo_list_data: TodoListUpdate) -> Optional[TodoList]:
        """
        Update an existing todo list.

        Args:
            todo_list_id: The ID of the todo list to update
            todo_list_data: New data for the todo list

        Returns:
            Updated TodoList object if found, None otherwise
        """
        for i, todo_list in enumerate(self._storage):
            if todo_list.id == todo_list_id:
                updated_todo_list = TodoList(id=todo_list_id, name=todo_list_data.name)
                self._storage[i] = updated_todo_list
                return updated_todo_list
        return None

    def delete(self, todo_list_id: int) -> bool:
        """
        Delete a todo list by ID.

        Args:
            todo_list_id: The ID of the todo list to delete

        Returns:
            True if deleted, False if not found
        """
        for i, todo_list in enumerate(self._storage):
            if todo_list.id == todo_list_id:
                self._storage.pop(i)
                return True
        return False

    def get_todos(self, todo_list_id: int) -> Optional[list[Todo]]:
        for todo_list in self._storage:
            if todo_list.id == todo_list_id:
                return todo_list.todos
        return None

    def process_toggle_complete_background(self, todo_list_id: int, completed: bool) -> None:
        """
        Background long-running toggle-complete.
        Notifies frontend through WebSocket.
        """
        event_loop = get_loop()
        try:
            todo_list = self.get(todo_list_id)

            if not todo_list:
                event_loop.call_soon_threadsafe(
                    lambda: (
                        asyncio.create_task(
                            websocket_manager.broadcast_retry(
                                todo_list_id,
                                {
                                    "event": "toggle_complete_error",
                                    "listId": todo_list_id,
                                    "error": "TodoList not found"
                                }
                            )
                        )
                    )
                )
                return

            todos = todo_list.todos or []

            for todo in todos:
                todo.completed = completed

            event_loop.call_soon_threadsafe(
                lambda: (
                    asyncio.create_task(
                        websocket_manager.broadcast_retry(
                            todo_list_id,
                            {
                                "event": "toggle_complete_done",
                                "listId": todo_list_id,
                                "completed": completed
                            }
                        )
                    )
                )
            )


        except Exception as err:
            captured_err = str(err)

            def _retry_task(err_msg: str = captured_err) -> None:
                asyncio.create_task(
                    websocket_manager.broadcast_retry(
                        todo_list_id,
                        {
                            "event": "toggle_complete_error",
                            "listId": todo_list_id,
                            "error": err_msg,
                        },
                    )
                )

            event_loop.call_soon_threadsafe(_retry_task)

        finally:
            del todos
            del todo_list

            self.unlock(todo_list_id)

# Global singleton instance
_todo_list_service: Optional[TodoListService] = None


def get_todo_list_service() -> TodoListService:
    """
    Get or create the singleton TodoListService instance.

    This function is used for dependency injection in FastAPI.

    Returns:
        The singleton TodoListService instance
    """
    global _todo_list_service
    if _todo_list_service is None:
        _todo_list_service = TodoListService()
    return _todo_list_service
