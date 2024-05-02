from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from site_ong.database import get_session
from site_ong.security import (
    create_access_token,
    get_current_user,
    verify_password,
)
from site_ong.templates_conf import templates
from site_ong.users.models import User

router = APIRouter(prefix='/login')

Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', response_class=HTMLResponse)
def login_page(request: Request, user: CurrentUser):
    if user:
        return RedirectResponse('/dashboard', status_code=303)

    return templates.TemplateResponse('login.html', {'request': request})


@router.post('/')
async def login(request: Request, session: Session, response: Response):
    form = await request.form()
    username = form.get('username')
    password = form.get('password')
    user = session.scalar(select(User).where(User.username == username))
    if not user:
        raise HTTPException(
            status_code=400, detail='Invalid username or password'
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=400, detail='Invalid username or password'
        )

    token = create_access_token({'sub': username})
    redirect_response = RedirectResponse('/dashboard', status_code=303)
    redirect_response.set_cookie(
        key='access_token', value=token, httponly=True, samesite='lax'
    )

    return redirect_response
