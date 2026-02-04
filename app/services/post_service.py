from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.models.post import Post


class PostService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_posts(self, posts: list[dict]):
        for item in posts:
            post_data = {"id": item["id"], "title": item["title"], "body": item["body"], "user_id": item.get("userId")}

            result = await self.session.execute(select(Post).where(Post.id == post_data["id"]))
            post = result.scalar_one_or_none()

            if post:
                post.title = post_data["title"]
                post.body = post_data["body"]
                post.user_id = post_data["user_id"]
            else:
                self.session.add(Post(**post_data))

        await self.session.commit()

    async def get_posts(self, offset: int = 0, limit: int = 100):
        result = await self.session.execute(select(Post).offset(offset).limit(limit))
        return result.scalars().all()
