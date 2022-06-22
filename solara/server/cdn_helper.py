import logging
import pathlib
import sys

import requests

logger = logging.getLogger("Solara.cdn")

cdn = "https://cdn.jsdelivr.net/npm/"

default_cache_dir = pathlib.Path(sys.prefix + "/share/_solara/cdn/")

cdn_url_path = "_solara/cdn"


def put_in_cache(base_cache_dir: pathlib.Path, path, data: bytes):
    cache_path = base_cache_dir / path
    pathlib.Path(cache_path.parent).mkdir(parents=True, exist_ok=True)
    try:
        logger.info("Writing cache file: %s", cache_path)
        cache_path.write_bytes(data)
    except FileNotFoundError:
        logger.info("Failed writing cache file: %s", cache_path)


def get_from_cache(base_cache_dir: pathlib.Path, path):
    cache_path = base_cache_dir / path
    try:
        logger.info("Opening cache file: %s", cache_path)
        return cache_path.read_bytes()
    except FileNotFoundError:
        pass


def get_cdn_url(path):
    return cdn + path


def get_data(base_cache_dir: pathlib.Path, path):
    parts = path.split("/")
    store_path = path if len(parts) != 1 else pathlib.Path(path) / "__main"

    content = get_from_cache(base_cache_dir, store_path)
    if content:
        return content

    url = get_cdn_url(path)
    response = requests.get(url)
    if response.ok:
        put_in_cache(base_cache_dir, store_path, response.content)
        return response.content
    else:
        logger.warning("Could not load URL: %r", url)
        raise Exception(f"Could not load URL: {url}")