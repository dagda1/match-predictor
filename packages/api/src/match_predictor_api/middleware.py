import os

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

ORIGIN_SECRET_ARN = os.environ.get("ORIGIN_SECRET_ARN")

_cached_secret: str | None = None


def _get_origin_secret() -> str | None:
    global _cached_secret
    if _cached_secret:
        return _cached_secret
    if not ORIGIN_SECRET_ARN:
        return None
    import boto3
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=ORIGIN_SECRET_ARN)
    _cached_secret = response["SecretString"]
    return _cached_secret


class OriginVerifyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "/_debug/" in request.url.path:
            return await call_next(request)
        secret = _get_origin_secret()
        if secret:
            if request.headers.get("x-origin-verify") != secret:
                return JSONResponse(status_code=403, content={"detail": "forbidden"})
        return await call_next(request)
