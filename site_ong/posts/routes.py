from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from site_ong.database import get_session
from site_ong.posts.models import Post
from site_ong.security import get_current_user
from site_ong.templates_conf import templates
from site_ong.users.models import User

router = APIRouter(prefix='/posts')

Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', response_class=HTMLResponse)
def blog(request: Request, session: Session):
    posts_db = session.query(Post).all()

    posts = [
        {
            'id': post.id,
            'title': post.title,
            'subhead': post.subhead,
            'posted_by': post.posted_by,
            'date_posted': post.date_posted.strftime('%d/%m/%Y'),
            'content': post.content,
        }
        for post in posts_db
    ]

    return templates.TemplateResponse(
        'blog.html', {'request': request, 'posts': posts}
    )


@router.get('/admin')
def admin_page(request: Request, user: CurrentUser, session: Session):
    if not user:
        return RedirectResponse('/login')
    posts = session.query(Post).all()
    return templates.TemplateResponse(
        'posts_admin.html', {'request': request, 'posts': posts}
    )


@router.get('/novo', response_class=HTMLResponse)
def new_post_page(request: Request, user: CurrentUser):
    if not user:
        return RedirectResponse('/login')
    return templates.TemplateResponse('new_post.html', {'request': request})


@router.post('/novo')
async def new_post(request: Request, user: CurrentUser, session: Session):
    if not user:
        return RedirectResponse('/login')

    form = await request.form()
    title = form.get('title')
    subhead = form.get('subhead')
    posted_by = form.get('author')
    content = form.get('editordata')

    post_db = Post(
        title=title, subhead=subhead, posted_by=posted_by, content=content
    )

    session.add(post_db)
    session.commit()
    session.refresh(post_db)

    return RedirectResponse('/posts', status_code=303)


@router.get('/deletar/{post_id}')
def delete_post(post_id: int, session: Session, user: CurrentUser):
    if not user:
        return RedirectResponse('/login')
    if user.role != 'admin':
        raise HTTPException(
            403, 'Você não tem permissão para acessar esta página'
        )

    post = session.query(Post).get(post_id)
    session.delete(post)
    session.commit()
    return RedirectResponse('/posts/admin')


@router.get('/editar/{post_id}', response_class=HTMLResponse)
def edit_post_page(
    post_id: int, request: Request, user: CurrentUser, session: Session
):
    if not user or user.role != 'admin':
        return RedirectResponse('/login')
    post = session.query(Post).get(post_id)
    return templates.TemplateResponse(
        'edit_post.html', {'request': request, 'post': post}
    )


@router.post('/editar/{post_id}')
async def edit_post(
    post_id: int, request: Request, user: CurrentUser, session: Session
):
    if not user or user.role != 'admin':
        return RedirectResponse('/login')

    form = await request.form()
    title = form.get('title')
    subhead = form.get('subhead')
    posted_by = form.get('author')
    content = form.get('editordata')

    post = session.query(Post).get(post_id)
    post.title = title
    post.subhead = subhead
    post.posted_by = posted_by
    post.content = content

    session.commit()

    return RedirectResponse('/posts/admin', status_code=303)


@router.get('/{post_id}', response_class=HTMLResponse)
def post(request: Request, post_id: int, session: Session):
    post_db = session.query(Post).get(post_id)
    post = post_db.__dict__

    post['date_posted'] = post_db.date_posted.strftime('%d/%m/%Y')

    return templates.TemplateResponse(
        'post.html', {'request': request, 'post': post}
    )
