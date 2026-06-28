# Asset Tracking

VitaDex can model renewable assets such as domains, repositories, deployment projects, subscriptions, licenses, contracts, and warranties without storing private data in the public repository.

The public core provides:

- `AssetRecord`: a generic Pydantic model for asset metadata.
- `AssetValue`: an optional estimated value model.
- `AssetReminder`: reminder rules expressed as days before expiry.
- `AssetIntegration`: placeholders for calendar, DNS, hosting, analytics, billing, or other future integrations.
- `AssetLink`: relationship edges between assets, such as a GitHub repository powering a domain or deploying to a Vercel project.
- `AssetService`: small in-memory helpers for sorting, expiry windows, reminder candidates, link lookups, missing-link queues, and summaries.

Real portfolios must live in the local runtime, not in Git. Public examples must use synthetic assets such as `.example` domains and fake providers.

See `examples/assets/domain-portfolio.yaml` for an anonymous fixture.

## Repository and deployment matching

Use these generic asset kinds for project reconciliation:

- `github_repository`
- `vercel_project`
- `lovable_project`
- `domain`

Repository inventory can be stored as `AssetRecord` items with `provider: GitHub`. Use `links` to express relationships to domains, deployment projects, or builder projects. Keep uncertain matches as `confidence: candidate` until the deployment provider inventory confirms them.
