from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends, Request, status
from fastapi.responses import RedirectResponse
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from site_ong.database import get_session
from site_ong.users.models import User

from .auth.schemas import TokenData
from .settings import Settings

settings = Settings()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encode_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encode_jwt


async def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
):
    token = request.cookies.get('access_token')

    redirect_response = RedirectResponse(
        '/login', status_code=status.HTTP_303_SEE_OTHER
    )

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get('sub')
        if not username:
            return None
        token_data = TokenData(username=username)
    except (DecodeError, ExpiredSignatureError):
        return None

    user = session.scalar(
        select(User).where(User.username == token_data.username)
    )

    if user is None:
        return redirect_response

    return user
