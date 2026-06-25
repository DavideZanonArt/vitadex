from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field

from vitadex.core.ids import new_id
from vitadex.core.time import now_iso


class AssetValue(BaseModel):
    currency: str = "USD"
    amount: float | None = None
    label: str | None = None
    upper_bound_exclusive: float | None = None


class AssetReminder(BaseModel):
    channel: Literal["calendar", "email", "popup", "task", "webhook"] = "calendar"
    days_before: int = Field(ge=0)
    enabled: bool = True


class AssetIntegration(BaseModel):
    name: str
    enabled: bool = False
    provider: str | None = None
    external_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssetRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("asset"))
    name: str
    kind: Literal["domain", "subscription", "license", "contract", "warranty", "other"] = "other"
    provider: str | None = None
    status: Literal["active", "watching", "paused", "archived"] = "active"
    owner_area: str = "personal"
    expires_on: date | None = None
    renews_automatically: bool | None = None
    estimated_value: AssetValue | None = None
    reminders: list[AssetReminder] = Field(default_factory=list)
    integrations: list[AssetIntegration] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
