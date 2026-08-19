import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning("%s %s | %s | %s", request.method, request.url.path, exc.status_code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.message, "data": None}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        if errors:
            error = errors[0]
            loc = [str(l) for l in error["loc"] if l not in ("body",)]
            field = " -> ".join(loc) if loc else "request"
            message = f"{field}: {error['msg']}"
        else:
            message = "Validation error"
        logger.warning("%s %s | 422 | %s", request.method, request.url.path, errors)
        return JSONResponse(
            status_code=422,
            content={"success": False, "message": message, "data": None}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("%s %s | 500 | %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Internal server error", "data": None}
        )
