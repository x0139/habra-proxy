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


def trade_mark(matched):
    word = matched.group()
    return "".join([word, '™'])


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


def inject_svg(soup):
    script = "<script type='text/javascript' async='' src='/static/js/svg.js'></script>"
    # head = soup.find('head')
    # head.append(script)

    soup.head.insert(len(soup.head.contents),
                     soup.new_tag('script', **{'type': 'text/javascript', 'src': '/static/js/svg.js', 'async': ''}))
    soup.head.insert(len(soup.head.contents),
                     soup.new_tag('script',
                                  **{'type': 'text/javascript', 'src': '/static/js/svg4everybody.min.js'}))
    soup.head.insert(len(soup.head.contents),
                     soup.new_tag('script', **{'type': 'text/javascript', 'src': '/static/js/svgrun.js', 'async': ''}))


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


def save_to_static(file: bytes, local_filepath: str):
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
            local_filepath = os.path.join(STATIC_ROOT, filepath, filename)
            if not os.path.isfile(local_filepath):
                create_dir_if_not_exist(local_filepath)
                save_to_static(file, local_filepath)

    await _download('link', **{'href': True})
    await _download('img', **{'src': True})


def change_static_location(soup: BeautifulSoup):
    def _change_resource(tag: str, field):
        for html_tag in soup.findAll(tag):
            try:
                if html_tag[field][:1] == '/' and html_tag[field][:2] != '/':
                    html_tag[field] = html_tag[field].replace('/', '/static/', 1)
                else:
                    html_tag[field] = html_tag[field].replace("https://habr.com/", "/static/")

            except KeyError:
                pass

    _change_resource('link', 'href')
    _change_resource('img', 'src')


async def download_favicon(url: str):
    file = await download_file(url)
    save_to_static(file, 'favicon.ico')
