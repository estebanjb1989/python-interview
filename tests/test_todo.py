"""Unit tests for TodoList API endpoints."""

from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.Todo import Todo
from app.services.todo import get_todo_service


@pytest.fixture
def mock_service() -> Generator[MagicMock, None, None]:
    """
    Create a mock Todo for testing.

    Yields:
        Mock service instance
    """
    mock = MagicMock()

    # Override the dependency
    def override_get_service() -> MagicMock:
        return mock

    app.dependency_overrides[get_todo_service] = override_get_service
    yield mock
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI app.

    Returns:
        TestClient instance
    """
    return TestClient(app)


class TestIndex:
    """Tests for GET /api/todolists/{todo_list_id} endpoint."""

    def test_returns_all_todos_from_todolist(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that index returns all todo lists."""
        # Arrange
        expected = [
            Todo(id=1, description="Awesome task 1", completed=False),
            Todo(id=2, description="Awesome task 2", completed=False),
        ]
        mock_service.all.return_value = expected

        # Act
        response = client.get("/api/todolists/1/todos")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["id"] == 1
        assert response.json()[0]["description"] == "Awesome task 1"
        assert response.json()[1]["id"] == 2
        assert response.json()[1]["description"] == "Awesome task 2"
        mock_service.all.assert_called_once()

    def test_returns_empty_list_when_no_todos(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that index returns empty list when no todos exist."""
        # Arrange
        mock_service.all.return_value = []

        # Act
        response = client.get("/api/todolists/1/todos")

        # Assert
        assert response.status_code == 200
        assert response.json() == []
        mock_service.all.assert_called_once()


class TestShow:
    """Tests for GET /api/todolists/{todo_list_id}/todo/{todo_id} endpoint."""

    def test_returns_todo_by_id(self, client: TestClient, mock_service: MagicMock) -> None:
        """Test that show returns a specific todo from a given todo list."""
        # Arrange
        expected_todo = Todo(id=1, description="Awesome task 1", completed=False)
        mock_service.get.return_value = expected_todo

        # Act
        response = client.get("/api/todolists/1/todos/1")

        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert response.json()["description"] == "Awesome task 1"
        assert not response.json()["completed"]
        mock_service.get.assert_called_once_with(1, 1)

    def test_returns_404_when_not_found(self, client: TestClient, mock_service: MagicMock) -> None:
        """Test that show returns 404 when todo doesn't exist."""
        # Arrange
        mock_service.get.return_value = None

        # Act
        response = client.get("/api/todolists/1/todos/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        mock_service.get.assert_called_once_with(1, 999)


class TestCreate:
    # """Tests for POST /api/todolists/{todo_list_id}/todos/{todo_id} endpoint."""

    def test_creates_new_todo(self, client: TestClient, mock_service: MagicMock) -> None:
        """Test that create successfully creates a new todo list."""
        # Arrange
        created_todo = Todo(id=1, description="Awesome task 1", completed=False)
        mock_service.create.return_value = created_todo

        # Act
        response = client.post(
            "/api/todolists/1/todos", json={"description": "Awesome task 1", "completed": False}
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["id"] == 1
        assert response.json()["description"] == "Awesome task 1"
        mock_service.create.assert_called_once()

    def test_validates_required_fields(self, client: TestClient, mock_service: MagicMock) -> None:
        """Test that create validates required fields."""
        # Act
        response = client.post("/api/todolists/1/todos", json={})

        # Assert
        assert response.status_code == 422
        print(response.status_code)
        mock_service.create.assert_not_called()

    def test_validates_name_not_empty(self, client: TestClient, mock_service: MagicMock) -> None:
        """Test that create validates name is not empty."""
        # Act
        response = client.post("/api/todolists/1/todos", json={"description": ""})

        # Assert
        assert response.status_code == 422
        mock_service.create.assert_not_called()


class TestUpdate:
    """Tests for PUT /api/todolists/{id} endpoint."""

    def test_updates_existing_todo(self, client: TestClient, mock_service: MagicMock) -> None:
        """Test that update successfully updates an existing todo."""
        # Arrange
        updated_todo = Todo(id=1, description="Updated todo", completed=True)
        mock_service.update.return_value = updated_todo

        # Act
        response = client.put(
            "/api/todolists/1/todos/1", json={"description": "Updated todo", "completed": "False"}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert response.json()["description"] == "Updated todo"
        assert response.json()["completed"]
        mock_service.update.assert_called_once()

    def test_returns_404_when_not_found(self, client: TestClient, mock_service: MagicMock) -> None:
        """Test that update returns 404 when todo doesn't exist."""
        # Arrange
        mock_service.update.return_value = None

        # Act
        response = client.put(
            "/api/todolists/1/todos/999", json={"description": "Updated", "completed": "False"}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        mock_service.update.assert_called_once()

    def test_validates_required_fields(self, client: TestClient, mock_service: MagicMock) -> None:
        """Test that update validates required fields."""
        # Act
        response = client.put("/api/todolists/1/todos/1", json={})

        # Assert
        assert response.status_code == 422
        mock_service.update.assert_not_called()


class TestDelete:
    """Tests for DELETE /api/todolists/{id}/todos endpoint."""

    def test_deletes_existing_todo(self, client: TestClient, mock_service: MagicMock) -> None:
        """Test that delete successfully deletes an existing todo."""
        # Arrange
        mock_service.delete.return_value = True

        # Act
        response = client.delete("/api/todolists/1/todos/1")

        # Assert
        assert response.status_code == 204
        assert response.content == b""
        mock_service.delete.assert_called_once_with(1, 1)

    def test_returns_404_when_not_found(self, client: TestClient, mock_service: MagicMock) -> None:
        """Test that delete returns 404 when todo list doesn't exist."""
        # Arrange
        mock_service.delete.return_value = False

        # Act
        response = client.delete("/api/todolists/1/todos/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        mock_service.delete.assert_called_once_with(1, 999)
