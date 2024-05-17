from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from typer import Typer

from site_ong.database import engine
from site_ong.security import get_password_hash
from site_ong.users.models import User

app = Typer()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@app.command()
def create():
    """Create admin/admin user"""
    session = SessionLocal()
    db_user = session.scalar(select(User).where(User.username == 'admin'))
    if db_user:
        session.delete(db_user)
        session.commit()

    hashed_password = get_password_hash('admin')
    db_user = User(
        full_name='Admin',
        username='admin',
        password=hashed_password,
        role='admin',
    )
    session.add(db_user)
    session.commit()
