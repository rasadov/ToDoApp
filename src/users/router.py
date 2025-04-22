from fastapi import APIRouter


router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post("/login")
async def login():
    pass

@router.post("/register")
async def register():
    pass

@router.post("/refresh")
async def refresh():
    pass

@router.post("/logout")
async def logout():
    pass
