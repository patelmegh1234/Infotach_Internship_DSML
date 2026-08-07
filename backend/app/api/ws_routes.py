# Megh, Upload Date: 2026-08-02
# WebSocket Routes: Real-Time Analysis Progress Streaming
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.task_manager import task_manager

ws_router = APIRouter()


@ws_router.websocket("/ws/{task_id}")
async def analysis_progress(websocket: WebSocket, task_id: str) -> None:
    """
    WebSocket endpoint that streams progress events for a running analysis task.

    Client connects immediately after POSTing to /api/analyze/submit.
    Events are JSON objects: {"stage": str, "progress": int, "status": str, ...}
    Final event includes the full analysis result under "result" key.
    """
    await websocket.accept()

    task = task_manager.get(task_id)
    if task is None:
        await websocket.send_json({"stage": "error", "status": "error", "error": "Task not found."})
        await websocket.close()
        return

    try:
        while True:
            try:
                # Wait up to 60 seconds for the next event from the task queue
                event = await asyncio.wait_for(task._queue.get(), timeout=60.0)
                await websocket.send_json(event)

                if event.get("status") in ("complete", "error"):
                    break
            except asyncio.TimeoutError:
                # Send keep-alive ping so connection doesn't drop
                await websocket.send_json({"stage": "heartbeat", "status": "running", "progress": task.progress})
    except WebSocketDisconnect:
        pass
    finally:
        # Clean up task after a short delay to allow reconnects
        await asyncio.sleep(5)
        task_manager.remove(task_id)
