from pydantic import BaseModel

class CreateTaskSchema(BaseModel):
    title: str
    description: str
    status: str
