from fastapi import FastAPI

from src.users.router import router as user_router
from src.tasks.router import router as task_router

app = FastAPI()

app.include_router(user_router)
app.include_router(task_router)
