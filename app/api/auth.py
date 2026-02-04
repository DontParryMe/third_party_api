from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..db.session import AsyncSessionLocal
from ..services.user_service import UserService
from ..core.security import create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


class AuthRequest(BaseModel):
    username: str
    password: str


async def get_user_service():
    async with AsyncSessionLocal() as session:
        yield UserService(session)


@router.post("/")
async def auth(
    auth_data: AuthRequest,
    service: UserService = Depends(get_user_service),
):
    user = await service.get_by_username(auth_data.username)

    if not user:
        user = await service.create_user(auth_data.username, auth_data.password)
    else:
        if not service.verify_password(auth_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}
