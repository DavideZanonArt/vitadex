# Contributing

Thanks for contributing to `vitadex`.

## Basic Rules

- No real personal data in the repository.
- No secrets, tokens, absolute local paths, or credentials in commits.
- All external actions must remain safe by default.
- Every change must preserve the separation between the public core and the local runtime.

## Development Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env.local
```

## Useful Commands

```bash
pytest
ruff check .
mypy vitadex
```

## Pull Request

- Keep PRs small and focused.
- Update documentation if you change setup, configuration, or user-facing behavior.
- Add or update tests when regression risk justifies it.
- Confirm explicitly that you are not introducing sensitive data.

## Scope

Welcome contributions:

- hardening for the local runtime
- safe-by-default integrations
- docs
- test
- CLI and dashboard UX improvements

Out-of-scope contributions without prior discussion:

- approval bypasses
- automation for payments, signatures, or legal commitments
- access to business contexts or production systems
