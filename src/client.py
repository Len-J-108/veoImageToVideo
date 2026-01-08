"""HTTP client for interacting with KieAI's VIE API."""

from __future__ import annotations

import logging
import time
from typing import Optional

import requests

from src.config import AppConfig
from src.models import GenerationRequest, TaskStatus, TaskSubmission

LOGGER = logging.getLogger(__name__)


class KieAIClient:
    """Simple wrapper around the VIE API endpoints."""

    def __init__(self, config: AppConfig) -> None:
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        self._base_url = config.base_url.rstrip("/")
        self._poll_interval = config.poll_interval_seconds
        self._timeout_seconds = config.timeout_seconds
        self._max_retries = config.max_retries
        self._backoff_seconds = config.retry_backoff_seconds

    def submit_generation(self, request: GenerationRequest) -> TaskSubmission:
        payload = request.to_payload()
        LOGGER.info(
            "Submitting generation request: model=%s duration=%ss aspect_ratio=%s",
            payload["model"],
            payload["duration"],
            payload["aspect_ratio"],
        )
        response_json = self._request("POST", "/tasks", json=payload)
        submission = TaskSubmission.from_api(response_json)
        LOGGER.info("Task %s generated, video processing...", submission.task_id)
        return submission

    def get_task_status(self, task_id: str) -> TaskStatus:
        LOGGER.debug("Fetching status for task %s", task_id)
        response_json = self._request("GET", f"/tasks/{task_id}")
        status = TaskStatus.from_api(response_json)
        return status

    def poll_until_complete(self, task_id: str) -> TaskStatus:
        LOGGER.info(
            "Polling task %s every %ss for up to %ss",
            task_id,
            self._poll_interval,
            self._timeout_seconds,
        )
        start_time = time.monotonic()
        last_state: Optional[str] = None

        while True:
            status = self.get_task_status(task_id)
            if status.status != last_state:
                LOGGER.info("Task %s status: %s", task_id, status.status)
                last_state = status.status

            if status.status == "completed":
                if not status.asset_url:
                    raise RuntimeError(
                        f"Task {task_id} reported completed but no asset URL was provided"
                    )
                LOGGER.info("Task %s completed successfully", task_id)
                return status

            if status.status == "failed":
                raise RuntimeError(
                    f"Task {task_id} failed: {status.error_message or 'Unknown error'}"
                )

            elapsed = time.monotonic() - start_time
            if elapsed > self._timeout_seconds:
                raise TimeoutError(
                    f"Polling timed out after {self._timeout_seconds}s for task {task_id}"
                )

            LOGGER.debug("Task %s still %s; sleeping %ss", task_id, status.status, self._poll_interval)
            time.sleep(self._poll_interval)

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self._base_url}{path}"
        attempt = 0
        while True:
            attempt += 1
            try:
                response = self._session.request(method, url, timeout=30, **kwargs)
                response.raise_for_status()
                json_body = response.json()
                return json_body
            except (requests.RequestException, ValueError) as exc:
                if attempt >= self._max_retries:
                    LOGGER.error("HTTP %s %s failed after %s attempts", method, url, attempt)
                    raise
                LOGGER.warning(
                    "HTTP %s %s failed on attempt %s: %s; retrying in %ss",
                    method,
                    url,
                    attempt,
                    exc,
                    self._backoff_seconds,
                )
                time.sleep(self._backoff_seconds)
