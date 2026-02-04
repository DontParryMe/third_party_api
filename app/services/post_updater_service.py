from ..core import logger
from ..db.session import AsyncSessionLocal
from ..services.post_service import PostService
from ..services.external_api import JSONPlaceholderAPI


class PostUpdaterService:
    def __init__(self):
        self.api = JSONPlaceholderAPI()

    async def update_data(self):
        try:
            posts = await self.api.fetch_posts()
            async with AsyncSessionLocal() as session:
                post_service = PostService(session)
                await post_service.upsert_posts(posts)
            logger.get_logger(__name__).info(f"Fetched and saved {len(posts)} posts")
        except Exception as e:
            logger.get_logger(__name__).error("Failed to update posts", exc_info=e)
