from fastapi import HTTPException
from starlette import status


class NotFoundException(HTTPException):
    def __init__(self, status_code: int = status.HTTP_404_NOT_FOUND, detail: str = "Resource not found"):
        super().__init__(status_code=status_code, detail=detail)


class UnAuthorizedException(HTTPException):
    def __init__(self, status_code: int = status.HTTP_401_UNAUTHORIZED, detail: str = "Unauthorized access"):
        super().__init__(status_code=status_code, detail=detail)


class BadRequestException(HTTPException):
    def __init__(self, status_code: int = status.HTTP_400_BAD_REQUEST, detail: str = "Bad request"):
        super().__init__(status_code=status_code, detail=detail)
