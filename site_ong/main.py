from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from site_ong.templates_conf import templates

app = FastAPI()

app.mount('/static', StaticFiles(directory='site_ong/static'), name='static')


@app.get('/', response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(name='index.html', request=request)
