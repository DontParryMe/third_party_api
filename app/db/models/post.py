from sqlalchemy import Column, Integer, String, Text

from ..base import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    title = Column(String(255))
    body = Column(Text)