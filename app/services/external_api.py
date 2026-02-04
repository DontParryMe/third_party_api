from ..services.http_client import HTTPClient


class JSONPlaceholderAPI:
    def __init__(self):
        self.client = HTTPClient("https://jsonplaceholder.typicode.com")

    async def fetch_posts(self):
        return await self.client.get("/posts")
