from http.client import responses

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.config.schemas import ErrorMSG


class Error_DB(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code


async def custom_exception_handler(request: Request, exc: Error_DB):
    error_schema = ErrorMSG(error_type=responses[exc.code], error_message=exc.message)
    return JSONResponse(status_code=exc.code, content=error_schema.model_dump())


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_type = "ValidationError"
    error_schema = ErrorMSG(error_type=error_type, error_message=repr(exc))
    return JSONResponse(
        error_schema.model_dump(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def response_validation_exception_handler(
    request: Request, exc: ResponseValidationError
):
    error_type = "ResponseValidationError"
    error_schema = ErrorMSG(error_type=error_type, error_message=repr(exc.errors()))
    return JSONResponse(
        error_schema.model_dump(),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def all_http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_schema = ErrorMSG(
        error_type=responses[exc.status_code], error_message=exc.detail
    )
    return JSONResponse(status_code=exc.status_code, content=error_schema.model_dump())
