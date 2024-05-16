from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
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
    if not user or user.role != 'admin':
        return RedirectResponse('/login')

    users = session.query(User).all()
    return templates.TemplateResponse(
        'users.html', {'request': request, 'users': users}
    )


@router.get('/novo', response_class=HTMLResponse)
def new_user_page(request: Request, user: CurrentUser):
    if not user or user.role != 'admin':
        return RedirectResponse('/login')
    return templates.TemplateResponse('new_user.html', {'request': request})


@router.post('/novo', response_class=HTMLResponse)
async def new_user(request: Request, user: CurrentUser, session: Session):
    if not user or user.role != 'admin':
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
    if not user or user.role != 'admin':
        return RedirectResponse('/login')
    return templates.TemplateResponse('delete_user.html', {'request': request})


@router.post('/deletar')
async def delete_user(request: Request, user: CurrentUser, session: Session):
    if not user or user.role != 'admin':
        return RedirectResponse('/login')

    form = await request.form()
    username = form.get('username')

    if username == user.username:
        return templates.TemplateResponse(
            'delete_user.html',
            {'request': request, 'error': 'Você não pode deletar a si mesmo.'},
        )

    user = session.query(User).filter(User.username == username).first()
    if user:
        session.delete(user)
        session.commit()
    else:
        return templates.TemplateResponse(
            'delete_user.html',
            {'request': request, 'error': 'Usuário não encontrado.'},
        )

    return RedirectResponse('/dashboard', status_code=303)


@router.get('/editar/{user_id}', response_class=HTMLResponse)
def edit_user_page(
    user_id: int, request: Request, user: CurrentUser, session: Session
):
    if not user or user.role != 'admin':
        return RedirectResponse('/login')

    user = session.scalar(select(User).where(User.id == user_id))
    return templates.TemplateResponse(
        'edit_user.html', {'request': request, 'user': user}
    )


@router.post('/editar/{user_id}')
async def edit_user(
    user_id: int, request: Request, user: CurrentUser, session: Session
):
    if not user or user.role != 'admin':
        return RedirectResponse('/login')

    form = await request.form()
    full_name = form.get('name')
    password = form.get('password')

    user = session.scalar(select(User).where(User.id == user_id))
    if user:
        user.full_name = full_name
        user.role = form.get('role')

        if password:
            user.password = get_password_hash(password)

        session.commit()
        session.refresh(user)
    else:
        return templates.TemplateResponse(
            'edit_user.html',
            {'request': request, 'error': 'Usuário não encontrado.'},
        )

    return RedirectResponse('/dashboard', status_code=303)
