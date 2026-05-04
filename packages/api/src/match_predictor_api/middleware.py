import os
import sys

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

ORIGIN_SECRET_ARN = os.environ.get("ORIGIN_SECRET_ARN")

_cached_secret: str | None = None


def _log(message: str) -> None:
    print(f"[OriginVerify] {message}", flush=True)
    sys.stdout.flush()


def _get_origin_secret() -> str | None:
    global _cached_secret
    if _cached_secret:
        _log("using cached secret")
        return _cached_secret
    if not ORIGIN_SECRET_ARN:
        _log("ORIGIN_SECRET_ARN not set, skipping fetch")
        return None
    _log(f"importing boto3 to fetch {ORIGIN_SECRET_ARN}")
    import boto3
    _log("creating secretsmanager client")
    client = boto3.client("secretsmanager")
    _log("calling get_secret_value")
    response = client.get_secret_value(SecretId=ORIGIN_SECRET_ARN)
    _log("get_secret_value returned, caching")
    _cached_secret = response["SecretString"]
    return _cached_secret


class OriginVerifyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "/_debug/" in request.url.path:
            return await call_next(request)
        _log(f"dispatch start path={request.url.path}")
        secret = _get_origin_secret()
        _log(f"secret resolved (present={secret is not None})")
        if secret:
            if request.headers.get("x-origin-verify") != secret:
                _log("header mismatch, returning 403")
                return JSONResponse(status_code=403, content={"detail": "forbidden"})
        _log("calling downstream handler")
        response = await call_next(request)
        _log(f"downstream returned status={response.status_code}")
        return response
