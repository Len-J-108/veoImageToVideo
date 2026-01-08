"""Utilities for composing narration and stage direction prompts."""

from __future__ import annotations

from src.config import AppConfig

PROMPT_TEMPLATE = """{stage}

Gesprochener Text (Deutsch): "{speech}"

Outro: {outro}

Visuelle Referenz: Die Szene beginnt mit einer Person, die auf einer Steinbank vor einer rauen Steinmauer sitzt. Nutze die Referenzaufnahme ({reference_url}) für Kleidung, Licht und Textur. Die Person soll im Video aufstehen, um die Bank herumgehen und währenddessen den obigen Text sprechen."""  # noqa: E501


def build_prompt(config: AppConfig) -> str:
    """Compose the final narrative and direction prompt."""

    prompt = PROMPT_TEMPLATE.format(
        stage=config.stage_direction,
        speech=config.speech_text,
        outro=config.outro_description,
        reference_url=config.reference_image_url,
    )

    return prompt.strip()
