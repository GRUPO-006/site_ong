from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from site_ong.database import Base


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    subhead: Mapped[str]
    posted_by: Mapped[str]
    date_posted: Mapped[datetime] = mapped_column(server_default=func.now())
    content: Mapped[str]
