"""Configuration helpers for the VEO image-to-video workflow."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)

REFERENCE_IMAGE_URL = (
    "https://storage.googleapis.com/kieai-assets/reference/bench-speaker.jpg"
)
GERMAN_SPEECH_TEXT = (
    "Ich laufe um die Bank, während ich ruhig erkläre, wie sich jeder Schritt "
    "nach vorne wie ein neues Kapitel anfühlt. Die Steinmauer hinter mir bleibt "
    "stark, und meine Stimme trägt über den Platz."  # noqa: E501
)
GERMAN_STAGE_DIRECTION = (
    "Die Person erhebt sich von einer Steinbank und beginnt langsam, den Rahmen zu umkreisen. "
    "Die Kamera bleibt hochkant, folgt jedem Schritt sanft und betont den Kontrast zwischen "
    "bewegter Figur und ruhiger Steinmauer."  # noqa: E501
)
GERMAN_OUTRO_DESCRIPTION = (
    "Zum Schluss bleibt die Person kurz stehen, legt die Hand auf die Banklehne und lächelt "
    "zuversichtlich in die Kamera, bevor sie aus dem Bild nach links verschwindet."  # noqa: E501
)


@dataclass(frozen=True)
class AppConfig:
    """Container for immutable application settings."""

    api_key: str
    base_url: str
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


def load_config() -> AppConfig:
    """Load application configuration from defaults and environment variables."""

    api_key = os.getenv("KIEAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Environment variable KIEAI_API_KEY must be set with a valid API key."
        )

    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    config = AppConfig(
        api_key=api_key,
        base_url=os.getenv("KIEAI_BASE_URL", "https://api.kieai.com/v1"),
        topic="stone-bench-walkthrough",
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
    )

    LOGGER.info(
        "Configuration loaded: topic=%s, duration=%ss, aspect_ratio=%s, results_dir=%s",
        config.topic,
        config.duration_seconds,
        config.aspect_ratio,
        config.results_dir,
    )

    return config
