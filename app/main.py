"""FastAPI application entry point."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.event_loop import set_event_loop
from app.routers import todo, todo_lists, ws


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    loop = asyncio.get_running_loop()
    set_event_loop(loop)

    yield

    # Cleanup

app = FastAPI(
    title="TodoList API",
    description="A simple Todo List API",
    version="1.0.0",
    lifespan=lifespan
)

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todo_lists.router)
app.include_router(todo.router)
app.include_router(ws.router)

@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"message": "TodoList API is running"}
