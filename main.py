import asyncio
import contextlib
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.core.logger import setup_logging
from app.core.swagger import custom_openapi
from app.db.base import Base
from app.db.session import engine
from app.api import auth, posts
from app.middleware.auth import AuthMiddleware
from app.services.post_updater_service import PostUpdaterService
from app.tasks.updater import BackgroundUpdater

setup_logging()
post_updater_service = PostUpdaterService()
updater = BackgroundUpdater(service=post_updater_service, interval_seconds=settings.UPDATE_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    task = asyncio.create_task(updater.start())

    yield

    await updater.stop()
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


app = FastAPI(title="Test API", lifespan=lifespan)
app.add_middleware(AuthMiddleware)
app.include_router(auth.router)
app.include_router(posts.router)

app.openapi = lambda: custom_openapi(app)
