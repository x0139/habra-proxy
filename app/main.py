from aiohttp import web

from app.settings import APP_PORT, STATIC_ROOT, IMAGES_ROOT
from app.views import *


def create_app():
    app = web.Application()
    app.add_routes([web.static('/static/', STATIC_ROOT)])
    # app.add_routes([web.static('/images/', IMAGES_ROOT)])
    app.add_routes([web.get('/favicon.ico', favicon, name='favicon')])
    app.add_routes([web.get('/{path:(.*)}', index, name='index')])

    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=APP_PORT)
