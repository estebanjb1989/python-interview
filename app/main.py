"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import todo, todo_lists

# Create FastAPI application instance
app = FastAPI(
    title="TodoList API",
    description="A simple Todo List API",
    version="1.0.0",
)

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(todo_lists.router)
app.include_router(todo.router)


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Simple message indicating the API is running
    """
    return {"message": "TodoList API is running"}
