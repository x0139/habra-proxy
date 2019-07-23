import re

from aiohttp import ClientSession

from app.settings import LOCAL_URL


async def get_page(url: str):
    async with ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


def trade_mark(text):
    s = text.group()
    return "".join([s, '™'])


def add_trademark_in_soup(soup):
    pattern = r"(?<![А-я])[А-я]{6}(?![А-я])"
    for element in soup.findAll(text=True):
        text = re.sub(pattern, trade_mark, element)
        element.replaceWith(text)


def change_url_location_in_soup(soup):
    for a in soup.findAll('a'):
        try:
            a['href'] = a['href'].replace("https://habr.com/ru/", LOCAL_URL)
        except KeyError:
            pass
