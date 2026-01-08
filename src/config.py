"""Configuration helpers for the VEO image-to-video workflow."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

LOGGER = logging.getLogger(__name__)

REFERENCE_IMAGE_URL = "https://ibb.co/jvpw5pCp"
GERMAN_SPEECH_TEXT = (
    "Hör mir bloß auf mit Pauperismus. Hier weiß schon lange keiner mehr wie er klarkommen soll"
)
GERMAN_STAGE_DIRECTION = "empört, motzend, energisch, mokierend"
GERMAN_OUTRO_DESCRIPTION = (
    "Zum Schluss bleibt die Person kurz stehen, legt die Hand auf die Banklehne und lächelt "
    "zuversichtlich in die Kamera, bevor sie aus dem Bild nach links verschwindet."  # noqa: E501
)
DEFAULT_IMAGE_URLS: Tuple[str, ...] = (REFERENCE_IMAGE_URL,)
DEFAULT_GENERATION_TYPE = "REFERENCE_2_VIDEO"


@dataclass(frozen=True)
class AppConfig:
    """Container for immutable application settings."""

    api_key: str
    api_root: str
    topic: str
    reference_image_url: str
    speech_text: str
    stage_direction: str
    outro_description: str
    duration_seconds: int
    aspect_ratio: str
    poll_interval_seconds: int
    timeout_seconds: int
    results_dir: Path
    model: str
    max_retries: int
    retry_backoff_seconds: int
    image_urls: tuple[str, ...]
    generation_type: str
    enable_translation: bool
    watermark: str | None
    callback_url: str | None
    seed: int | None


def _normalize_api_root(raw_url: str) -> str:
    cleaned = raw_url.strip()
    if not cleaned:
        raise RuntimeError("KIEAI_BASE_URL must not be empty when provided.")
    cleaned = cleaned.rstrip("/")
    if cleaned.endswith("/generate"):
        cleaned = cleaned[: -len("/generate")]
    return cleaned


def load_config() -> AppConfig:
    """Load application configuration from defaults and environment variables."""

    api_key = os.getenv("KIEAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Environment variable KIEAI_API_KEY must be set with a valid API key."
        )

    raw_base_url = os.getenv(
        "KIEAI_BASE_URL",
        "https://api.kie.ai/api/v1/veo/generate",
    )
    api_root = _normalize_api_root(raw_base_url)

    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    config = AppConfig(
        api_key=api_key,
        api_root=api_root,
        topic="Pauperismus",
        reference_image_url=REFERENCE_IMAGE_URL,
        speech_text=GERMAN_SPEECH_TEXT,
        stage_direction=GERMAN_STAGE_DIRECTION,
        outro_description=GERMAN_OUTRO_DESCRIPTION,
        duration_seconds=8,
        aspect_ratio="9:16",
        poll_interval_seconds=20,
        timeout_seconds=10 * 60,
        results_dir=results_dir,
        model="veo3",
        max_retries=3,
        retry_backoff_seconds=3,
        image_urls=DEFAULT_IMAGE_URLS,
        generation_type=DEFAULT_GENERATION_TYPE,
        enable_translation=True,
        watermark=None,
        callback_url=None,
        seed=None,
    )

    LOGGER.info(
        "Configuration loaded: topic=%s, duration=%ss, aspect_ratio=%s, results_dir=%s",
        config.topic,
        config.duration_seconds,
        config.aspect_ratio,
        config.results_dir,
    )

    LOGGER.info("Using API root %s (raw env value %s)", config.api_root, raw_base_url)

    return config

