from urllib.parse import urljoin

from aiohttp.web_response import Response
from bs4 import BeautifulSoup

from app.utils import get_page, add_trademark_in_soup, change_url_location_in_soup


async def index(request):
    """
    Get habr.com page (include path), change text and replace href
    :param request:
    :return:
    """
    path = request.match_info.get('path')
    url = urljoin('https://habr.com/ru/', path)

    habra_html = await get_page(url)

    soup = BeautifulSoup(habra_html, "html5lib")

    add_trademark_in_soup(soup)

    change_url_location_in_soup(soup)

    return Response(text=soup.prettify()[4:], content_type='text/html')
