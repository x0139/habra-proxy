import os
import pathlib

APP_PORT = 8232

LOCAL_URL = "http://localhost:{}/".format(APP_PORT)

HABRA_FAVICON = 'https://habr.com/favicon.ico'
HABRA_URL = 'https://habr.com/ru/'

PROJECT_ROOT = pathlib.Path(__file__).parent.parent
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
IMAGES_ROOT = os.path.join(PROJECT_ROOT, 'static', 'images')
