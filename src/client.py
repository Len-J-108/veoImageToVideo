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
        self._api_root = config.api_root.rstrip("/")
        self._poll_interval = config.poll_interval_seconds
        self._timeout_seconds = config.timeout_seconds
        self._max_retries = config.max_retries
        self._backoff_seconds = config.retry_backoff_seconds

    def submit_generation(self, request: GenerationRequest) -> TaskSubmission:
        payload = request.to_payload()
        LOGGER.info(
            "Submitting generation request: model=%s aspect_ratio=%s generation_type=%s",
            payload["model"],
            payload["aspectRatio"],
            payload["generationType"],
        )
        response_json = self._request("POST", "/generate", json=payload)
        self._ensure_api_success(response_json, "generate")
        submission = TaskSubmission.from_api(response_json)
        LOGGER.info("Task %s generated, video processing...", submission.task_id)
        return submission

    def get_task_status(self, task_id: str) -> TaskStatus:
        LOGGER.debug("Fetching status for task %s", task_id)
        response_json = self._request(
            "GET",
            "/record-info",
            params={"taskId": task_id},
        )
        self._ensure_api_success(response_json, "record-info")
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
        last_flag: Optional[int] = None

        while True:
            status = self.get_task_status(task_id)
            if status.success_flag != last_flag:
                LOGGER.info(
                    "Task %s success_flag=%s error_code=%s",
                    task_id,
                    status.success_flag,
                    status.error_code,
                )
                last_flag = status.success_flag

            if status.is_complete:
                asset_url = status.asset_url
                if not asset_url:
                    raise RuntimeError(
                        f"Task {task_id} reported success but did not return result URLs"
                    )
                LOGGER.info("Task %s completed successfully", task_id)
                return status

            if status.success_flag in {2, 3}:
                raise RuntimeError(
                    f"Task {task_id} failed (code={status.error_code}): {status.error_message}"
                )

            elapsed = time.monotonic() - start_time
            if elapsed > self._timeout_seconds:
                raise TimeoutError(
                    f"Polling timed out after {self._timeout_seconds}s for task {task_id}"
                )

            LOGGER.debug(
                "Task %s still processing (flag=%s); sleeping %ss",
                task_id,
                status.success_flag,
                self._poll_interval,
            )
            time.sleep(self._poll_interval)

    def _endpoint(self, path: str) -> str:
        return f"{self._api_root}{path}"

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = self._endpoint(path)
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

    @staticmethod
    def _ensure_api_success(response_json: dict, operation: str) -> None:
        code = response_json.get("code")
        if code != 200:
            msg = response_json.get("msg")
            raise RuntimeError(
                f"KieAI {operation} call failed with code {code}: {msg}"
            )
