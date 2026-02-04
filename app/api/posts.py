from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import get_session
from ..services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/")
async def get_posts(
    offset: int = Query(0, description="offset"),
    limit: int = Query(100, description="limit"),
    session: AsyncSession = Depends(get_session),
):
    service = PostService(session)
    return await service.get_posts(offset=offset, limit=limit)
