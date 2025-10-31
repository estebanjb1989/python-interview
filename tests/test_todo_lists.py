"""Unit tests for TodoList API endpoints."""

from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import TodoList
from app.services.todo_lists import get_todo_list_service


@pytest.fixture
def mock_service() -> Generator[MagicMock, None, None]:
    """
    Create a mock TodoListService for testing.

    Yields:
        Mock service instance
    """
    mock = MagicMock()

    # Override the dependency
    def override_get_service() -> MagicMock:
        return mock

    app.dependency_overrides[get_todo_list_service] = override_get_service
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
    """Tests for GET /api/todolists endpoint."""

    def test_returns_all_todo_lists(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that index returns all todo lists."""
        # Arrange
        expected_todos = [
            TodoList(id=1, name="First list"),
            TodoList(id=2, name="Second list"),
        ]
        mock_service.all.return_value = expected_todos

        # Act
        response = client.get("/api/todolists")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["id"] == 1
        assert response.json()[0]["name"] == "First list"
        assert response.json()[1]["id"] == 2
        assert response.json()[1]["name"] == "Second list"
        mock_service.all.assert_called_once()

    def test_returns_empty_list_when_no_todos(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that index returns empty list when no todos exist."""
        # Arrange
        mock_service.all.return_value = []

        # Act
        response = client.get("/api/todolists")

        # Assert
        assert response.status_code == 200
        assert response.json() == []
        mock_service.all.assert_called_once()


class TestShow:
    """Tests for GET /api/todolists/{id} endpoint."""

    def test_returns_todo_list_by_id(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that show returns a specific todo list."""
        # Arrange
        expected_todo = TodoList(id=1, name="Test list")
        mock_service.get.return_value = expected_todo

        # Act
        response = client.get("/api/todolists/1")

        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert response.json()["name"] == "Test list"
        mock_service.get.assert_called_once_with(1)

    def test_returns_404_when_not_found(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that show returns 404 when todo list doesn't exist."""
        # Arrange
        mock_service.get.return_value = None

        # Act
        response = client.get("/api/todolists/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        mock_service.get.assert_called_once_with(999)


class TestCreate:
    """Tests for POST /api/todolists endpoint."""

    def test_creates_new_todo_list(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that create successfully creates a new todo list."""
        # Arrange
        created_todo = TodoList(id=1, name="New list")
        mock_service.create.return_value = created_todo

        # Act
        response = client.post("/api/todolists", json={"name": "New list"})

        # Assert
        assert response.status_code == 201
        assert response.json()["id"] == 1
        assert response.json()["name"] == "New list"
        mock_service.create.assert_called_once()

    def test_validates_required_fields(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that create validates required fields."""
        # Act
        response = client.post("/api/todolists", json={})

        # Assert
        assert response.status_code == 422
        mock_service.create.assert_not_called()

    def test_validates_name_not_empty(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that create validates name is not empty."""
        # Act
        response = client.post("/api/todolists", json={"name": ""})

        # Assert
        assert response.status_code == 422
        mock_service.create.assert_not_called()


class TestUpdate:
    """Tests for PUT /api/todolists/{id} endpoint."""

    def test_updates_existing_todo_list(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that update successfully updates an existing todo list."""
        # Arrange
        updated_todo = TodoList(id=1, name="Updated list")
        mock_service.update.return_value = updated_todo

        # Act
        response = client.put("/api/todolists/1", json={"name": "Updated list"})

        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert response.json()["name"] == "Updated list"
        mock_service.update.assert_called_once()

    def test_returns_404_when_not_found(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that update returns 404 when todo list doesn't exist."""
        # Arrange
        mock_service.update.return_value = None

        # Act
        response = client.put("/api/todolists/999", json={"name": "Updated"})

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        mock_service.update.assert_called_once()

    def test_validates_required_fields(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that update validates required fields."""
        # Act
        response = client.put("/api/todolists/1", json={})

        # Assert
        assert response.status_code == 422
        mock_service.update.assert_not_called()


class TestDelete:
    """Tests for DELETE /api/todolists/{id} endpoint."""

    def test_deletes_existing_todo_list(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that delete successfully deletes an existing todo list."""
        # Arrange
        mock_service.delete.return_value = True

        # Act
        response = client.delete("/api/todolists/1")

        # Assert
        assert response.status_code == 204
        assert response.content == b""
        mock_service.delete.assert_called_once_with(1)

    def test_returns_404_when_not_found(
        self, client: TestClient, mock_service: MagicMock
    ) -> None:
        """Test that delete returns 404 when todo list doesn't exist."""
        # Arrange
        mock_service.delete.return_value = False

        # Act
        response = client.delete("/api/todolists/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        mock_service.delete.assert_called_once_with(999)
