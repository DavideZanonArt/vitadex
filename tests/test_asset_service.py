from __future__ import annotations

from datetime import date

from vitadex.models.asset import AssetLink, AssetRecord, AssetReminder, AssetValue
from vitadex.services.asset_service import AssetService


def test_asset_service_sorts_and_filters_expiring_assets():
    service = AssetService(
        [
            AssetRecord(name="later.example", kind="domain", expires_on=date(2027, 6, 15), renews_automatically=True),
            AssetRecord(name="soon.example", kind="domain", expires_on=date(2027, 5, 10), renews_automatically=False),
            AssetRecord(name="software license", kind="license", expires_on=date(2027, 5, 20)),
        ]
    )

    expiring = service.expiring_between(date(2027, 5, 1), date(2027, 5, 31), kind="domain")

    assert [asset.name for asset in expiring] == ["soon.example"]


def test_asset_service_finds_reminder_candidates():
    asset = AssetRecord(
        name="renewal.example",
        kind="domain",
        expires_on=date(2027, 5, 10),
        reminders=[AssetReminder(channel="calendar", days_before=7)],
    )

    candidates = AssetService([asset]).reminder_candidates(date(2027, 5, 3))

    assert candidates == [(asset, 7)]


def test_asset_service_summary_counts_manual_renewals_and_value_model():
    service = AssetService(
        [
            AssetRecord(
                name="manual.example",
                kind="domain",
                expires_on=date(2027, 5, 10),
                renews_automatically=False,
                estimated_value=AssetValue(currency="USD", amount=250, label="$250"),
            ),
            AssetRecord(name="expired.example", kind="domain", expires_on=date(2027, 4, 1), renews_automatically=True),
        ]
    )

    summary = service.summary(date(2027, 5, 1))

    assert summary == {
        "total": 2,
        "active": 2,
        "expired": 1,
        "expiring_30_days": 1,
        "manual_renewal": 1,
    }


def test_asset_service_tracks_repository_links_to_domains_and_deployments():
    repository = AssetRecord(
        name="example-web",
        kind="github_repository",
        provider="GitHub",
        links=[
            AssetLink(target="example-alpha.example", target_kind="domain", relationship="powers", confidence="confirmed"),
            AssetLink(target="example-web-prod", target_kind="vercel_project", relationship="deploys", confidence="candidate"),
        ],
    )
    service = AssetService(
        [
            AssetRecord(name="example-alpha.example", kind="domain"),
            AssetRecord(name="example-web-prod", kind="vercel_project"),
            repository,
            AssetRecord(name="unmatched-repo", kind="github_repository"),
        ]
    )

    assert service.linked_to("example-alpha.example", target_kind="domain") == [repository]
    assert service.linked_to("example-web-prod", confidence="confirmed") == []
    assert [asset.name for asset in service.missing_links("github_repository")] == ["unmatched-repo"]
