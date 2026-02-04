from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
import jwt
from jwt import PyJWTError

from app.db.session import AsyncSessionLocal
from app.services.user_service import UserService
from app.core.config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(p) for p in ["/auth", "/docs", "/openapi.json", "/redoc"]):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Authorization header missing"}, status_code=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise ValueError("Missing sub claim")
        except (PyJWTError, ValueError):
            return JSONResponse({"detail": "Invalid or expired token"}, status_code=status.HTTP_401_UNAUTHORIZED)

        async with AsyncSessionLocal() as session:
            service = UserService(session)
            user = await service.get_by_id(int(user_id))
            if not user:
                return JSONResponse({"detail": "User not found"}, status_code=status.HTTP_401_UNAUTHORIZED)

        request.state.user = user

        response = await call_next(request)
        return response
