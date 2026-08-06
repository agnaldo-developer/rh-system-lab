import logging
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


def build_error_response(
        
    *,
    status_code: int,
    message: str,
    path: str,
    details: Any | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {
        "status_code": status_code,
        "message": message,
        "path": path,
        
    }
    if request_id is not None:
        error["request_id"] = request_id

    if details is not None:
        error["details"] = details

    return {
        "error": error,
    }


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            path=request.url.path,
            request_id=getattr(
                request.state,
                "request_id",
                None,
            ),
        ),
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=build_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message="Request validation failed.",
            path=request.url.path,
            details=exc.errors(),
            request_id=getattr(
                request.state,
                "request_id",
                None,
            ),
        ),
    )

async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled application exception",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error.",
            path=request.url.path,
            request_id=getattr(
            request.state,
                "request_id",
                None,
            ),
        ),
    )
