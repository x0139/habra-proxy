import os
from urllib.parse import urljoin

from aiohttp import web
from aiohttp.web_response import Response
from bs4 import BeautifulSoup

from app.settings import HABRA_URL, STATIC_ROOT, HABRA_FAVICON
from app.utils import get_page, add_trademark, change_url_location, download_static, \
    change_static_location, download_favicon, inject_svg


async def index(request):
    """
    Get habr.com page (include path), change text and replace href
    :param request:
    :return:
    """
    path = request.match_info.get('path')
    url = urljoin(HABRA_URL, path)

    habra_html = await get_page(url)

    soup = BeautifulSoup(habra_html, "html5lib")

    add_trademark(soup)

    change_url_location(soup)

    # await download_static(soup)
    # #
    # change_static_location(soup)
    inject_svg(soup)

    return Response(text=soup.prettify()[4:], content_type='text/html')


async def favicon(request):
    favi = await download_favicon(HABRA_FAVICON)
    return web.FileResponse(os.path.join(STATIC_ROOT, 'favicon.ico'))
