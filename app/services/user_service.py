from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.db.models.user import User


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ph = PasswordHasher()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, username: str, password: str) -> User:
        hashed = self.ph.hash(password)
        user = User(username=username, hashed_password=hashed)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    def verify_password(self, password: str, hashed_password: str) -> bool:
        try:
            self.ph.verify(hashed_password, password)
            return True
        except VerifyMismatchError:
            return False
