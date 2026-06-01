from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.error import BadRequestErrorDetail, BadRequestErrorResponse


class NotFoundError(Exception):
    def __init__(self, message: str = "Not found"):
        self.message = message


class ForbiddenError(Exception):
    def __init__(self, message: str = "Forbidden"):
        self.message = message


class ConflictError(Exception):
    def __init__(self, message: str = "Conflict"):
        self.message = message


class UnprocessableError(Exception):
    def __init__(self, message: str = "Unprocessable entity"):
        self.message = message


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(FastAPIHTTPException)
    async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
        # If detail is already a dict (e.g. {"message": "..."}), pass it through directly
        if isinstance(exc.detail, dict):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": str(exc.detail)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        details = []
        for error in exc.errors():
            loc = error.get("loc", [])
            # Skip the "body" prefix in loc if present
            field = str(loc[-1]) if loc else "unknown"
            details.append(
                BadRequestErrorDetail(
                    field=field,
                    message=error.get("msg", ""),
                    type=error.get("type", ""),
                )
            )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=BadRequestErrorResponse(
                message="Validation failed",
                details=details,
            ).model_dump(),
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": exc.message},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": exc.message},
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": exc.message},
        )

    @app.exception_handler(UnprocessableError)
    async def unprocessable_handler(request: Request, exc: UnprocessableError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": exc.message},
        )
