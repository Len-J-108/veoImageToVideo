"""Utilities for composing narration and stage direction prompts."""

from __future__ import annotations

from src.config import AppConfig

PROMPT_TEMPLATE = """{stage}

Gesprochener Text (Deutsch): "{speech}"

Outro: {outro}

Visuelle Referenz: Die Szene beginnt mit einer Person, die auf einer antiken Bank vor einer rauen Steinmauer sitzt. Die Person soll im Video aufstehen und währenddessen den obigen Text sprechen."


def build_prompt(config: AppConfig) -> str:
    """Compose the final narrative and direction prompt."""

    prompt = PROMPT_TEMPLATE.format(
        stage=config.stage_direction,
        speech=config.speech_text,
        outro=config.outro_description,
        reference_url=config.reference_image_url,
    )

    return prompt.strip()
