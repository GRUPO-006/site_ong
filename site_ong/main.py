from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from site_ong.auth.routes import router as auth_router
from site_ong.dashboard.routes import router as dashboard_router
from site_ong.database import engine
from site_ong.posts.routes import router as posts_router
from site_ong.security import get_password_hash
from site_ong.templates_conf import templates
from site_ong.users.models import User
from site_ong.users.routes import router as users_router

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    yield


app = FastAPI(lifespan=lifespan)

app.mount('/static', StaticFiles(directory='site_ong/static'), name='static')

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(posts_router)
app.include_router(users_router)


@app.get('/', response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(name='index.html', request=request)


@app.get('/contato', response_class=HTMLResponse)
def contato(request: Request):
    return templates.TemplateResponse(name='contato.html', request=request)


@app.get('/logout', response_class=HTMLResponse)
def logout(request: Request):
    response = RedirectResponse(url='/', status_code=303)
    response.delete_cookie('access_token')
    return response
