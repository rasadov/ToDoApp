from fastapi import HTTPException
from starlette import status


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(status_code=status_code, detail=detail)


class UnAuthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized access", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)


class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)
