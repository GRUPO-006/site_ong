from typing import Literal

from sqlalchemy.orm import Mapped, mapped_column

from site_ong.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role: Mapped[Literal['admin', 'writer']]
