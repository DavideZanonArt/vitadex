# Asset Tracking

VitaDex can model renewable assets such as domains, subscriptions, licenses, contracts, and warranties without storing private data in the public repository.

The public core provides:

- `AssetRecord`: a generic Pydantic model for asset metadata.
- `AssetValue`: an optional estimated value model.
- `AssetReminder`: reminder rules expressed as days before expiry.
- `AssetIntegration`: placeholders for calendar, DNS, hosting, analytics, billing, or other future integrations.
- `AssetService`: small in-memory helpers for sorting, expiry windows, reminder candidates, and summaries.

Real portfolios must live in the local runtime, not in Git. Public examples must use synthetic assets such as `.example` domains and fake providers.

See `examples/assets/domain-portfolio.yaml` for an anonymous fixture.
