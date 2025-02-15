import logging.config

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.common import logger, settings
from src.common.errors import ApplicationError
from src.common.exception_handlers import error_handler, request_validation_error_handler
from src.middleware.cors import get_cors_middleware
from src.routers.base import router


def setup_exception_handlers(app: FastAPI) -> None:
    del app.exception_handlers[RequestValidationError]
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(ApplicationError, error_handler)


def app_setup(app: FastAPI) -> None:
    setup_exception_handlers(app)


def init_app() -> FastAPI:
    log_config = logger.make_logger_conf(settings.settings.log_config)
    if not settings.settings.DEBUG:
        logging.config.dictConfig(log_config)
    app = FastAPI(
        debug=settings.settings.DEBUG,
        title=settings.settings.SERVICE_NAME,
        middleware=[get_cors_middleware(settings.settings.CORS_ORIGINS)],
    )
    app.include_router(router)
    app_setup(app)
    return app
