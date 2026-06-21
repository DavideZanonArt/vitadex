# private-os

[![CI](https://github.com/DavideZanonArt/private-os-public/actions/workflows/ci.yml/badge.svg)](https://github.com/DavideZanonArt/private-os-public/actions/workflows/ci.yml)
[![Secret Scan](https://github.com/DavideZanonArt/private-os-public/actions/workflows/secret-scan.yml/badge.svg)](https://github.com/DavideZanonArt/private-os-public/actions/workflows/secret-scan.yml)

Locale-first framework for building a personal agent OS with memory, tasks, plans, approvals, follow-ups, audit logs, and Codex integration.

The public repository contains the product core. Personal data, real memory, logs, and user-specific configuration must remain local and outside version control.

## Features

- Operational tasks with status, goal, constraints, assumptions, and next actions.
- Structured memory with review workflows, sensitivity levels, and local search.
- Approval queue for all external actions.
- Persistent follow-ups and audit logs.
- Read-only CLI and web dashboards.
- Exportable and reusable skills.
- Local Codex harness integration running in `dry_run` and `fail_closed` mode.

## Requirements

- Python 3.12+
- a Unix-like local environment or macOS
- no business credentials stored in the repository

## Installation

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env.local
./scripts/bootstrap-local.sh
private-os init
```

## Secure Local Configuration

The public repository must not contain personal data. Always use an untracked local overlay:

```bash
cp .env.example .env.local
```

Configure at least these local paths:

- `PRIVATE_OS_STATE_ROOT`
- `PRIVATE_OS_DATA_DIR`
- `PRIVATE_OS_MEMORY_DIR`
- `PRIVATE_OS_LOG_DIR`
- `PRIVATE_OS_WORKSPACE_DIR`
- `PRIVATE_OS_DB_PATH`

Recommended example:

```env
PRIVATE_OS_STATE_ROOT=~/.private-os
PRIVATE_OS_DATA_DIR=~/.private-os/data
PRIVATE_OS_MEMORY_DIR=~/.private-os/memory
PRIVATE_OS_LOG_DIR=~/.private-os/logs
PRIVATE_OS_WORKSPACE_DIR=~/.private-os/workspace
PRIVATE_OS_DB_PATH=~/.private-os/data/private_os.sqlite
```

Do not commit `.env.local`. The same rule applies to `memory/`, `housing/`, `workspace/`, `logs/`, the SQLite database, and any file containing personal content.

## Quickstart

```bash
private-os init
private-os memory add --type preference --area travel --text "I prefer road trips with reliable Wi-Fi."
private-os task create --title "Prepare temporary apartment request" --area home --goal "Collect options and outreach drafts"
private-os task plan <task_id>
private-os task execute <task_id> --dry-run
private-os approvals list
private-os dashboard
private-os web
private-os codex status
```

## Security Model

Safe mode is enabled by default:

- browser runs in mock or search-plan mode
- Gmail creates drafts and does not send messages
- Calendar creates proposals instead of real events
- Drive uses mock local storage
- Telegram generates mock notifications
- filesystem access is limited to the configured scope
- payments, signatures, and legal commitments are forbidden

## Repository Model

The intended structure is:

- `public repo`: code, tests, documentation, anonymized examples, base configuration
- `local instance`: user profile, real memory, real tasks, runtime outputs, local overrides
- `Codex`: attached to the local instance, not to published data

## Main Structure

- `private_os/`: Python implementation
- `tests/`: automated tests
- `config/`: versioned policies and defaults
- `docs/`: architecture, local setup, and integrations
- `examples/`: anonymous fixtures
- `templates/`: generic templates
- `workflows/`: documented workflows

## Included Skills

- `housing_search`
- `quote_request`
- `travel_planning`
- `appointment_booking`
- `document_request`
- `complaint_management`
- `purchase_research`
- `email_followup`
- `decision_matrix`
- `dashboard_digest`

## Codex Integration

`private-os codex ...` binds a local task to a Codex thread. The core keeps tasks, memory, approvals, follow-ups, and audit logs; Codex owns the agent session and workspace changes.

See `docs/future-openclaw-integration.md` and `private_os/integrations/codex_harness/README.md`.
For the canonical local workflow, see `docs/codex-local-workflow.md`.

## Development

```bash
pytest
ruff check .
mypy private_os
```

To add a skill:

1. Create `private_os/skills/<skill>.py`.
2. Extend `Skill`.
3. Define `manifest`.
4. Implement `plan()` and `execute()`.
5. Register the skill in `private_os/skills/__init__.py`.
6. Add workflow, templates, and tests.

## Contributions

Open issues or pull requests following `CONTRIBUTING.md`. PRs must not contain personal data, secrets, absolute local paths, or real examples traceable to actual people.

## Post-Publish Operations

See `docs/post-publish-checklist.md` for the GitHub and runtime steps to maintain after publishing.

## License

Vedi `LICENSE`.
