import os
from urllib.parse import urljoin

from aiohttp import web
from aiohttp.web_response import Response
from bs4 import BeautifulSoup

from app.settings import HABRA_URL, STATIC_ROOT, HABRA_FAVICON
from app.utils import get_page, add_trademark, change_url_location, \
    download_favicon, change_use_xlink


async def index(request):
    """
    Get habr.com page (include path), change text and replace href
    :param request:
    :return:
    """
    path = request.match_info.get('path')
    url = urljoin(HABRA_URL, path)

    habra_html, status = await get_page(url)

    soup = BeautifulSoup(habra_html, "html5lib")

    add_trademark(soup)

    change_url_location(soup)

    change_use_xlink(soup)

    return Response(text=soup.prettify()[4:], content_type='text/html', status=status)


async def favicon(request):
    favi = await download_favicon(HABRA_FAVICON)
    return web.FileResponse(os.path.join(STATIC_ROOT, 'favicon.ico'))
