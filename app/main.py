from aiohttp import web

from app.settings import APP_PORT
from app.views import index


def create_app():
    app = web.Application()
    app.add_routes([web.get('/{path:(.*)}', index, name='index')])
    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=APP_PORT)
