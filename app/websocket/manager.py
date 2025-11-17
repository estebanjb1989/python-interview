import asyncio

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, set[WebSocket]] = {}

    async def connect(self, list_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        if list_id not in self.active_connections:
            self.active_connections[list_id] = set()
        self.active_connections[list_id].add(websocket)

    def disconnect(self, list_id: int, websocket: WebSocket) -> None:
        if list_id in self.active_connections:
            self.active_connections[list_id].discard(websocket)

            if len(self.active_connections[list_id]) == 0:
                del self.active_connections[list_id]

    async def broadcast(self, list_id: int, message: dict[str, object]) -> None:
        if list_id not in self.active_connections:
            return

        for ws in list(self.active_connections[list_id]):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(list_id, ws)

    async def broadcast_retry(
        self,
        list_id: int,
        message: dict[str, object],
        retries: int = 10,
        delay: float = 0.1
    ) -> None:
        """
        Retries broadcast until at least one client is connected.
        Useful when server reloads and WS connects slightly after the background task.
        """
        for attempt in range(retries):
            conns = self.active_connections.get(list_id)

            print(f"[WS RETRY] attempt={attempt} connections={0 if conns is None else len(conns)}")

            if conns and len(conns) > 0:
                return await self.broadcast(list_id, message)

            await asyncio.sleep(delay)

websocket_manager: WebSocketManager = WebSocketManager()
