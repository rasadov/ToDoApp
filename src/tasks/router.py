from fastapi import APIRouter


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

@router.get("/{task_id}")
async def get_task(task_id: int):
    pass

@router.get("/list")
async def list_tasks():
    pass

@router.post("/create")
async def create_task():
    pass

@router.put("/{task_id}")
async def update_task(task_id: int):
    pass

@router.delete("/{task_id}")
async def delete_task(task_id: int):
    pass