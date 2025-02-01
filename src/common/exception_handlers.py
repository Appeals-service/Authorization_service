from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from common.errors import ApplicationError, ObjectNotFoundError, RequestDataError
from dto.schemas.exception import HandledExceptionSchema, HandledValidationExceptionSchema


def _generate_exception_handler(schema: HandledExceptionSchema | HandledValidationExceptionSchema):
    return JSONResponse(content=schema.model_dump(), status_code=schema.status)


def error_handler(_: Request, exc: ObjectNotFoundError | RequestDataError | ApplicationError) -> JSONResponse:
    schema = HandledExceptionSchema(message=exc.message, status=exc.status, context=exc.context)
    return _generate_exception_handler(schema)


def request_validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    schema = HandledValidationExceptionSchema(
        message="Невозможно обработать тело/параметры запроса",
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        context=jsonable_encoder(exc.errors()),
    )
    return _generate_exception_handler(schema)
