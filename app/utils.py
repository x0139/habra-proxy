import os
import re
from typing import Tuple

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from app.settings import LOCAL_URL, STATIC_ROOT, HABRA_URL


async def get_page(url: str):
    async with ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text(), resp.status


def trade_mark(matched):
    word = matched.group()
    return "".join([word, '™'])


def add_trademark(soup: BeautifulSoup):
    pattern = r"(\b\w{6}\b)|(?<![А-яёЁ])[А-яёЁ]{6}(?![А-яёЁ])"

    soup.exclude_tags = []

    def title():
        title = soup.find('title', text=True)
        text = re.sub(pattern, trade_mark, title.string)
        title.decompose()
        new_tag = soup.new_tag("title")
        new_tag.string = text
        soup.head.insert(0, new_tag)

    def body():
        for element in soup.body(text=True):
            text = re.sub(pattern, trade_mark, element)
            element.replaceWith(text)

    title()
    body()


def change_a_href(soup: BeautifulSoup):
    for a in soup.findAll('a', 'href' is not None):
        a['href'] = a['href'].replace("https://habr.com/ru/", LOCAL_URL)


async def download_file(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            file_data = await resp.read()
            return file_data


def get_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    return filename


def get_filepath_from_url(url: str) -> str:
    parsed = urlparse(url)
    return os.path.dirname(parsed.path)


def save_to_static(file: bytes, local_filepath: str):
    try:
        with open(local_filepath, "wb") as local_file:
            local_file.write(file)
    except (IsADirectoryError, FileNotFoundError, PermissionError):
        pass


async def download_favicon(url: str):
    file = await download_file(url)
    save_to_static(file, os.path.join(STATIC_ROOT, 'favicon.ico'))


def change_static_location(soup: BeautifulSoup):
    def _change_resource(tag: str, field):
        for html_tag in soup.findAll(tag, field is not None):
            if html_tag[field][:1] == '/' and html_tag[field][:2] != '/':
                html_tag[field] = html_tag[field].replace('/', '/static/', 1)

    _change_resource('link', 'href')


def change_use_xlink(soup: BeautifulSoup):
    for use in soup.findAll('use'):
        use['xlink:href'] = use['xlink:href'].replace('https://habr.com/images/1564419171/', '/static/images/')


def change_font_face_location(soup: BeautifulSoup):
    for style in soup.findAll('style', attrs={'type': 'text/css'}):
        style.string = style.string.replace('/fonts/', '/static/fonts/')
