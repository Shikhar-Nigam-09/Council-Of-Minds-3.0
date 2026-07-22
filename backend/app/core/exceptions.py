from fastapi import Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

class InvalidCredentialsError(AppError):
    def __init__(self, message: str = "Incorrect email or password"):
        super().__init__(code="INVALID_CREDENTIALS", message=message, status_code=401)

class UserAlreadyExistsError(AppError):
    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(code="USER_ALREADY_EXISTS", message=message, status_code=400)

class TokenExpiredError(AppError):
    def __init__(self, message: str = "Token has expired"):
        super().__init__(code="TOKEN_EXPIRED", message=message, status_code=401)

class InvalidTokenError(AppError):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(code="INVALID_TOKEN", message=message, status_code=401)
        
class UserNotFoundError(AppError):
    def __init__(self, message: str = "User not found"):
        super().__init__(code="USER_NOT_FOUND", message=message, status_code=404)

async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.code, "message": exc.message}},
    )

async def generic_exception_handler(request: Request, exc: Exception):
    import logging
    logging.getLogger("app").exception(exc)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}},
    )
