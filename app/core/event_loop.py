import asyncio
from typing import Optional

event_loop: Optional[asyncio.AbstractEventLoop] = None

def set_event_loop(loop: asyncio.AbstractEventLoop) -> None:
    global event_loop
    event_loop = loop

def get_loop() -> asyncio.AbstractEventLoop:
    assert event_loop is not None, "Event loop has not been initialized"
    return event_loop
