from urllib.parse import urljoin

from aiohttp import web
from aiohttp.web_response import Response
from bs4 import BeautifulSoup

from app.settings import HABRA_URL
from app.utils import get_page, add_trademark_in_soup, change_url_location_in_soup, get_favicon


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

    add_trademark_in_soup(soup)

    change_url_location_in_soup(soup)

    return Response(text=soup.prettify()[4:], content_type='text/html')


async def favicon(request):
    favi = await get_favicon(HABRA_URL)
    return web.FileResponse(favi.read())
