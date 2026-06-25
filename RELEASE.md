# Release Process

Use this checklist before tagging a public release.

## Local Verification

```bash
pytest
ruff check .
mypy vitadex
cd dashboard-web
npm test -- --run
npm run lint
npm run build
```

If local mypy cache is corrupted, use a temporary cache:

```bash
mypy --cache-dir /tmp/vitadex-mypy-cache vitadex
```

## Privacy Review

Run these checks before publishing:

```bash
git status --short
git ls-files | rg '(^|/)(memory|housing|workspace|logs|.*\.db|.*\.sqlite|\.env\.local)$'
detect-secrets scan --baseline .secrets.baseline
```

The repository must not include personal memory, real tasks, runtime logs, SQLite databases, `.env.local`, private documents, screenshots with real data, or credentials.

## Versioning

1. Update `CHANGELOG.md`.
2. Confirm `pyproject.toml` contains the intended version.
3. Commit the release changes.
4. Tag the release:

```bash
git tag v0.1.0
git push origin main --tags
```

## GitHub Setup

After the first push, enable branch protection, required CI, Dependabot alerts, Dependabot security updates, and secret scanning where available.
