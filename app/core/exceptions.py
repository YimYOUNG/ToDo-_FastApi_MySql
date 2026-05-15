from fastapi import HTTPException, status


class TodoAppException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(TodoAppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedError(TodoAppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(TodoAppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class DuplicateError(TodoAppException):
    def __init__(self, field: str = "Field"):
        super().__init__(
            f"{field} already exists",
            status_code=status.HTTP_409_CONFLICT
        )
