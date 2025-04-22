from pydantic import BaseModel

class CreateUserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
