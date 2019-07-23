from aiohttp import web

from app.settings import APP_PORT
from app.views import *


def create_app():
    app = web.Application()
    app.add_routes([web.get('/{path:(.*)}', index, name='index')])
    app.add_routes([web.get('/favicon.ico', favicon, name='favicon')])
    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=APP_PORT)
