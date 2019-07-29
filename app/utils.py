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
    for element in soup.findAll(text=True):
        text = re.sub(pattern, trade_mark, element)
        element.replaceWith(text)


def change_url_location(soup: BeautifulSoup):
    for a in soup.findAll('a'):
        try:
            a['href'] = a['href'].replace("https://habr.com/ru/", LOCAL_URL)
        except KeyError:
            pass


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
    save_to_static(file, 'favicon.ico')


def change_use_xlink(soup):
    for use in soup.findAll('use'):
        use['xlink:href'] = use['xlink:href'].replace('https://habr.com/images/1564133473/', '/static/images/')
