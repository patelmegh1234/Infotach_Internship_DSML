# Megh, Upload Date: 2026-08-02
# In-Memory Task Manager for WebSocket Progress Streaming
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisTask:
    task_id: str
    stage: str = "queued"
    progress: int = 0          # 0-100
    status: str = "pending"    # pending | running | complete | error
    result: dict[str, Any] | None = None
    error: str | None = None
    _queue: asyncio.Queue = field(default_factory=asyncio.Queue, repr=False)


class TaskManager:
    """Singleton that stores in-flight analysis tasks keyed by task_id."""

    def __init__(self) -> None:
        self._tasks: dict[str, AnalysisTask] = {}

    def create(self) -> AnalysisTask:
        task_id = str(uuid.uuid4())
        task = AnalysisTask(task_id=task_id)
        self._tasks[task_id] = task
        return task

    def get(self, task_id: str) -> AnalysisTask | None:
        return self._tasks.get(task_id)

    async def push(self, task: AnalysisTask, stage: str, progress: int) -> None:
        task.stage = stage
        task.progress = progress
        await task._queue.put({"stage": stage, "progress": progress, "status": task.status})

    async def complete(self, task: AnalysisTask, result: dict[str, Any]) -> None:
        task.status = "complete"
        task.result = result
        task.progress = 100
        task.stage = "complete"
        await task._queue.put({"stage": "complete", "progress": 100, "status": "complete", "result": result})

    async def fail(self, task: AnalysisTask, error: str) -> None:
        task.status = "error"
        task.error = error
        await task._queue.put({"stage": "error", "progress": 0, "status": "error", "error": error})

    def remove(self, task_id: str) -> None:
        self._tasks.pop(task_id, None)


# Module-level singleton shared across the app
task_manager = TaskManager()
