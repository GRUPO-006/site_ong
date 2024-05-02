from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from site_ong.security import get_current_user
from site_ong.templates_conf import templates
from site_ong.users.models import User

router = APIRouter(prefix='/dashboard')

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', response_class=HTMLResponse)
def dashboard(request: Request, response: Response, user: CurrentUser):
    if not user:
        return RedirectResponse('/login', status_code=303)

    return templates.TemplateResponse(
        'dashboard.html',
        {'request': request, 'response': response, 'user': user},
    )
