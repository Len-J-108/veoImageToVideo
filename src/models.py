"""Shared request/response models for the VEO API client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

TaskState = Literal["queued", "processing", "completed", "failed"]


@dataclass(frozen=True)
class GenerationRequest:
    """Payload required to request a new video generation task."""

    model: str
    prompt: str
    duration_seconds: int
    aspect_ratio: str
    reference_image_url: str

    def to_payload(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "prompt": self.prompt,
            "duration": self.duration_seconds,
            "aspect_ratio": self.aspect_ratio,
            "reference_image_url": self.reference_image_url,
        }


@dataclass(frozen=True)
class TaskSubmission:
    """Response returned when a task is successfully created."""

    task_id: str

    @classmethod
    def from_api(cls, payload: Dict[str, Any]) -> "TaskSubmission":
        return cls(task_id=str(payload["task_id"]))


@dataclass(frozen=True)
class TaskStatus:
    """Snapshot of a task's current progress."""

    task_id: str
    status: TaskState
    asset_url: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def from_api(cls, payload: Dict[str, Any]) -> "TaskStatus":
        return cls(
            task_id=str(payload["task_id"]),
            status=payload.get("status", "processing"),
            asset_url=payload.get("asset_url"),
            error_message=payload.get("error"),
        )
