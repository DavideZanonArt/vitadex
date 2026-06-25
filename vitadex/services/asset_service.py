from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta

from vitadex.models.asset import AssetRecord


class AssetService:
    def __init__(self, assets: Iterable[AssetRecord] | None = None):
        self.assets = list(assets or [])

    def add(self, asset: AssetRecord) -> AssetRecord:
        self.assets.append(asset)
        return asset

    def list(self, kind: str | None = None, status: str | None = None) -> list[AssetRecord]:
        assets = self.assets
        if kind:
            assets = [asset for asset in assets if asset.kind == kind]
        if status:
            assets = [asset for asset in assets if asset.status == status]
        return sorted(assets, key=lambda asset: (asset.expires_on or date.max, asset.name))

    def expiring_between(self, start: date, end: date, kind: str | None = None) -> list[AssetRecord]:
        return [
            asset
            for asset in self.list(kind=kind)
            if asset.expires_on is not None and start <= asset.expires_on <= end
        ]

    def reminder_candidates(self, today: date) -> list[tuple[AssetRecord, int]]:
        candidates: list[tuple[AssetRecord, int]] = []
        for asset in self.list():
            if asset.expires_on is None:
                continue
            days_until_expiry = (asset.expires_on - today).days
            for reminder in asset.reminders:
                if reminder.enabled and days_until_expiry == reminder.days_before:
                    candidates.append((asset, reminder.days_before))
        return candidates

    def summary(self, today: date) -> dict[str, int]:
        active = self.list(status="active")
        return {
            "total": len(self.assets),
            "active": len(active),
            "expired": len([asset for asset in active if asset.expires_on is not None and asset.expires_on < today]),
            "expiring_30_days": len(self.expiring_between(today, today + timedelta(days=30))),
            "manual_renewal": len([asset for asset in active if asset.renews_automatically is False]),
        }
