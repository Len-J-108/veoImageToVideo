"""Helpers for streaming finished MP4 assets to disk."""

from __future__ import annotations

import logging
from pathlib import Path

import requests

LOGGER = logging.getLogger(__name__)
CHUNK_SIZE = 256 * 1024


def download_asset(asset_url: str, target_path: Path) -> Path:
    """Stream the MP4 asset provided by the API to disk."""

    LOGGER.info("Processing finished, downloading asset from %s", asset_url)
    with requests.get(asset_url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with target_path.open("wb") as file_obj:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if not chunk:
                    continue
                file_obj.write(chunk)

    LOGGER.info("Video saved to %s", target_path)
    return target_path
