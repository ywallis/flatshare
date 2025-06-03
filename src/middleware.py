from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from src.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        log_dict = {"url": request.url.path, "method": request.method}
        logger.info(log_dict)

        response = await call_next(request)
        return response
