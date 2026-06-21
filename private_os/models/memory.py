from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from private_os.core.ids import new_id
from private_os.core.time import now_iso

MemoryArea = Literal[
    "identity",
    "preferences",
    "constraints",
    "people",
    "places",
    "travel",
    "home",
    "car",
    "health",
    "finance",
    "bureaucracy",
    "writing_style",
    "decisions",
    "dislikes",
    "recurring_patterns",
    "private_projects",
    "relationships",
    "task_patterns",
    "do_not_do",
    "main",
    "shared",
    "private_profile",
]


class MemoryRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("mem"))
    text: str
    canonical_text: str | None = None
    type: str
    area: MemoryArea
    confidence: Literal["low", "medium", "high"] = "medium"
    source: Literal[
        "user_explicit", "user_implicit", "assistant_inferred", "imported", "system"
    ] = "user_explicit"
    sensitivity: Literal["public", "personal", "sensitive", "highly_sensitive"] = "personal"
    scope: Literal[
        "global",
        "private_life",
        "travel",
        "home",
        "health",
        "finance",
        "bureaucracy",
        "communication",
    ] = "private_life"
    tags: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    expires_at: str | None = None
    active: bool = True
    evidence: str | None = None
    notes: str | None = None
    related_task_id: str | None = None
    related_person: str | None = None
    review_status: Literal["accepted", "needs_review", "rejected"] = "accepted"

    def model_post_init(self, __context: object) -> None:
        if self.canonical_text is None:
            self.canonical_text = self.text.strip()
        if self.source == "assistant_inferred":
            self.review_status = "needs_review"
        if self.sensitivity in {"sensitive", "highly_sensitive"} and self.source != "user_explicit":
            self.review_status = "needs_review"
