"""Entrypoint orchestrating the image-to-video generation workflow."""

from __future__ import annotations

import logging
import sys

from src.client import KieAIClient
from src.config import load_config
from src.downloader import download_asset
from src.models import GenerationRequest
from src.prompt_builder import build_prompt


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def run() -> None:
    logger = logging.getLogger(__name__)
    config = load_config()
    prompt = build_prompt(config)
    logger.info("Prompt composed for topic %s", config.topic)

    client = KieAIClient(config)
    request = GenerationRequest(
        prompt=prompt,
        image_urls=config.image_urls,
        model=config.model,
        aspect_ratio=config.aspect_ratio,
        generation_type=config.generation_type,
        enable_translation=config.enable_translation,
        watermark=config.watermark,
        callback_url=config.callback_url,
        seed=config.seed,
    )

    submission = client.submit_generation(request)
    task_status = client.poll_until_complete(submission.task_id)
    asset_url = task_status.asset_url
    if not asset_url:
        raise RuntimeError(
            f"Task {task_status.task_id} completed but no asset URL was returned"
        )

    output_path = config.results_dir / f"{config.topic}-intro.mp4"
    download_asset(asset_url, output_path)

    logger.info("Workflow completed; video available at %s", output_path)


def main() -> int:
    configure_logging()
    try:
        run()
        return 0
    except Exception as exc:  # pylint: disable=broad-except
        logging.getLogger(__name__).exception("Workflow failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
