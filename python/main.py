from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import asyncio
import os
import logging

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Task:
    id: int
    title: str
    description: str
    done: bool
    created_at: datetime = field(default_factory=datetime.now)

class TaskStore:
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id = 1
        self._lock = asyncio.Lock()

    async def create(self, title: str, description: str = "") -> Task:
        async with self._lock:
            task = Task(
                id=self._next_id,
                title=title,
                description=description,
                done=False,
            )
            self._tasks[self._next_id] = task
            self._next_id += 1
            return task

    async def get(self, task_id: int) -> Optional[Task]:
        async with self._lock:
            return self._tasks.get(task_id)

    async def list(self) -> list[Task]:
        async with self._lock:
            return list(self._tasks.values())

    async def update(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        done: Optional[bool] = None,
    ) -> Optional[Task]:
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if done is not None:
                task.done = done
            return task

    async def delete(self, task_id: int) -> bool:
        async with self._lock:
            if task_id not in self._tasks:
                return False
            del self._tasks[task_id]
            return True

store = TaskStore()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Python server starting...")
    yield
    logger.info("Python server shutting down...")

app = FastAPI(title="Task API (Python)", lifespan=lifespan)

class TaskCreate(BaseModel):
    title: str
    description: str = ""

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    done: bool
    created_at: datetime

    class Config:
        from_attributes = True

def task_to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        done=task.done,
        created_at=task.created_at,
    )

@app.get("/healthz")
async def health():
    return {"status": "ok"}

@app.get("/tasks")
async def list_tasks():
    tasks = await store.list()
    return {"tasks": [task_to_response(t) for t in tasks]}

@app.post("/tasks", status_code=201)
async def create_task(payload: TaskCreate):
    task = await store.create(payload.title, payload.description)
    return task_to_response(task)

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    task = await store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="not found")
    return task_to_response(task)

@app.patch("/tasks/{task_id}")
async def update_task(task_id: int, payload: TaskUpdate):
    task = await store.update(
        task_id,
        title=payload.title,
        description=payload.description,
        done=payload.done,
    )
    if not task:
        raise HTTPException(status_code=404, detail="not found")
    return task_to_response(task)

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    if not await store.delete(task_id):
        raise HTTPException(status_code=404, detail="not found")
    return Response(status_code=204)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = asyncio.get_event_loop().time()
    response = await call_next(request)
    duration = asyncio.get_event_loop().time() - start
    logger.info(f"{request.method} {request.url.path} {duration:.3f}s")
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)