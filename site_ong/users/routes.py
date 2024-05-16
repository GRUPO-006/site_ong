from http.client import HTTPException
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from site_ong.auth.routes import CurrentUser
from site_ong.database import get_session
from site_ong.security import get_password_hash
from site_ong.templates_conf import templates
from site_ong.users.models import User

router = APIRouter(prefix='/usuarios')

Session = Annotated[Session, Depends(get_session)]


@router.get('/', response_class=HTMLResponse)
def users(request: Request, user: CurrentUser, session: Session):
    if not user:
        return RedirectResponse('/login')

    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Permissão negada')

    users = session.query(User).all()
    return templates.TemplateResponse(
        'users.html', {'request': request, 'users': users}
    )


@router.get('/novo', response_class=HTMLResponse)
def new_user_page(request: Request, user: CurrentUser):
    if not user:
        return RedirectResponse('/login')
    return templates.TemplateResponse('new_user.html', {'request': request})


@router.post('/novo', response_class=HTMLResponse)
async def new_user(request: Request, user: CurrentUser, session: Session):
    if not user:
        return RedirectResponse('/login')

    form = await request.form()
    full_name = form.get('name')
    username = form.get('username')
    password = form.get('password')
    role = form.get('role')

    db_user = User(
        full_name=full_name,
        username=username,
        password=get_password_hash(password),
        role=role,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return RedirectResponse('/dashboard', status_code=303)


@router.get('/deletar', response_class=HTMLResponse)
def delete_user_page(request: Request, user: CurrentUser):
    if not user:
        return RedirectResponse('/login')
    return templates.TemplateResponse('delete_user.html', {'request': request})


@router.post('/deletar')
async def delete_user(request: Request, user: CurrentUser, session: Session):
    if not user:
        return RedirectResponse('/login')

    form = await request.form()
    username = form.get('username')

    user = session.query(User).filter(User.username == username).first()
    if user:
        session.delete(user)
        session.commit()

    return RedirectResponse('/dashboard', status_code=303)


@router.get('/editar', response_class=HTMLResponse)
def edit_user_page(request: Request, user: CurrentUser):
    if not user:
        return RedirectResponse('/login')
    return templates.TemplateResponse('edit_user.html', {'request': request})


@router.post('/editar')
async def edit_user(request: Request, user: CurrentUser, session: Session):
    if not user:
        return RedirectResponse('/login')

    form = await request.form()
    username = form.get('username')
    new_username = form.get('new_username')
    new_password = form.get('new_password')
    user = session.query(User).filter(User.username == username).first()
    if user:
        user.username = new_username
        user.password = get_password_hash(new_password)
        session.commit()

    return RedirectResponse('/dashboard', status_code=303)
