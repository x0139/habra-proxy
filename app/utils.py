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
            return await resp.text()


def trade_mark(text):
    s = text.group()
    return "".join([s, '™'])


def add_trademark(soup: BeautifulSoup):
    pattern = r"(?<![А-яёЁ])[А-я]{6}(?![А-яёЁ])"
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


def create_dir_if_not_exist(path):
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            pass


def save_to_static(file: bytes, filepath: str, filename: str):
    local_filepath = os.path.join(STATIC_ROOT, filepath, filename)
    create_dir_if_not_exist(local_filepath)

    try:
        with open(local_filepath, "wb") as local_file:
            local_file.write(file)
    except (IsADirectoryError, FileNotFoundError, PermissionError):
        pass


async def download_static(soup: BeautifulSoup):
    async def _download(tag: str, **kwargs):
        for link in soup.find_all(tag, **kwargs):
            url = link[list(kwargs.keys())[0]]
            if url.startswith(''):
                url = urljoin(HABRA_URL, url)
            file = await download_file(url)
            filepath = get_filepath_from_url(url)[1:]
            filename = get_filename_from_url(url)
            save_to_static(file, filepath, filename)

    await _download('link', **{'href': True})
    await _download('img', **{'src': True})


def change_static_location(soup: BeautifulSoup):
    for link in soup.findAll('link'):
        try:
            if link['href'][:1] == '/':
                link['href'] = link['href'].replace('/', '/static/', 1)
            else:
                link['href'] = link['href'].replace("https://habr.com/", "/static/")

        except KeyError:
            pass

    for img in soup.findAll('img'):
        try:
            if img['src'][:1] == '/':
                img['src'] = img['href'].replace('/', '/static/', 1)
            else:
                img['src'] = img['src'].replace("https://habr.com/", "/static/")

        except KeyError:
            pass


async def download_favicon(url: str):
    file = await download_file(url)
    save_to_static(file, '', 'favicon.ico')
