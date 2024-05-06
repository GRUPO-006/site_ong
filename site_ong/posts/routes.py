from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from site_ong.templates_conf import templates

router = APIRouter(prefix='/post')


@router.get('/new_post', response_class=HTMLResponse)
def new_post_page(request: Request):
    return templates.TemplateResponse('new_post.html', {'request': request})
