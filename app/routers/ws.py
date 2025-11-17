import asyncio

from fastapi import APIRouter, WebSocket

from app.websocket.manager import websocket_manager

router = APIRouter(prefix="/ws")

ALLOWED_WS_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}

@router.websocket("/todolists/{todo_list_id}")
async def todo_list_ws(websocket: WebSocket, todo_list_id: int) -> None:
    origin = websocket.headers.get("origin")

    if origin not in ALLOWED_WS_ORIGINS:
        await websocket.close(code=403)
        return

    await websocket_manager.connect(int(todo_list_id), websocket)

    try:
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                await websocket.send_json({"event": "ping"})
    except Exception:
        websocket_manager.disconnect(int(todo_list_id), websocket)
