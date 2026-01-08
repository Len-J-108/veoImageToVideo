"""Shared request/response models for the VEO API client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class GenerationRequest:
    """Payload required to request a new video generation task."""

    prompt: str
    image_urls: Tuple[str, ...]
    model: str
    aspect_ratio: str
    generation_type: str
    enable_translation: bool
    watermark: Optional[str] = None
    callback_url: Optional[str] = None
    seed: Optional[int] = None

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "prompt": self.prompt,
            "imageUrls": list(self.image_urls),
            "model": self.model,
            "aspectRatio": self.aspect_ratio,
            "generationType": self.generation_type,
            "enableTranslation": self.enable_translation,
        }
        if self.callback_url:
            payload["callBackUrl"] = self.callback_url
        if self.watermark:
            payload["watermark"] = self.watermark
        if self.seed is not None:
            payload["seeds"] = self.seed
        return payload


@dataclass(frozen=True)
class TaskSubmission:
    """Response returned when a task is successfully created."""

    task_id: str

    @classmethod
    def from_api(cls, payload: Dict[str, Any]) -> "TaskSubmission":
        data = payload.get("data") or {}
        task_id = data.get("taskId")
        if not task_id:
            raise ValueError("Task submission response missing taskId")
        return cls(task_id=str(task_id))


@dataclass(frozen=True)
class TaskStatus:
    """Snapshot of a task's current progress."""

    task_id: str
    success_flag: int
    result_urls: Tuple[str, ...]
    origin_urls: Tuple[str, ...]
    error_code: Optional[int]
    error_message: Optional[str]

    @classmethod
    def from_api(cls, payload: Dict[str, Any]) -> "TaskStatus":
        data = payload.get("data") or {}
        response_block = data.get("response") or {}
        result_urls: List[str] = response_block.get("resultUrls") or []
        origin_urls: List[str] = response_block.get("originUrls") or []
        task_id = data.get("taskId")
        if not task_id:
            raise ValueError("Task status response missing taskId")
        return cls(
            task_id=str(task_id),
            success_flag=int(data.get("successFlag", 0)),
            result_urls=tuple(result_urls),
            origin_urls=tuple(origin_urls),
            error_code=data.get("errorCode"),
            error_message=data.get("errorMessage"),
        )

    @property
    def is_complete(self) -> bool:
        return self.success_flag == 1 and bool(self.result_urls)

    @property
    def asset_url(self) -> Optional[str]:
        return self.result_urls[0] if self.result_urls else None
