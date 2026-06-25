# Architecture

## Boundary Model

`vitadex` enforces a clear split between:

- versioned public core
- untracked local runtime

## Public Core

The core contains:

- Python code
- tests
- documentation
- base configuration
- anonymous examples

## Local Runtime

The runtime contains:

- real memory
- real tasks
- logs
- workspace
- SQLite database
- local overrides

The runtime is configured with `.env.local` and `VITADEX_STATE_ROOT`. It should live outside the repository or in ignored local paths. Public code may read from it at runtime, but public commits must never include its contents.

## Operational Flow

1. an input creates or updates a task
2. the system retrieves relevant memory
3. it selects a skill
4. it produces a plan
5. it executes only in `dry_run` when the action is external
6. it generates approvals and follow-ups
7. it records the audit log

## Components

```text
CLI / web dashboard
  calls services and renders read-only operational views

Services
  manage tasks, memory, approvals, follow-ups, planning, panels, and audit logs

Models
  define typed records with Pydantic

Storage
  uses SQLite for structured records and Markdown files for local memory exports

Skills
  map task intents to plans, dry-run outputs, approvals, and follow-ups

Integrations
  default to mock, draft, dry-run, or fail-closed modes
```

## Data Flow

```text
input
  -> TaskRecord
  -> memory search
  -> skill matching
  -> plan
  -> dry-run execution
  -> approvals and follow-ups
  -> audit log
  -> CLI/dashboard views
```

## Security Invariants

- External actions require explicit approvals.
- The public repository contains only generic examples and templates.
- Local runtime paths are ignored and documented as non-publishable.
- Codex harness execution defaults to `dry_run` and `fail_closed`.
- The web dashboard is local-first and guarded by a generated access token.

## Codex Integration

Codex works on the local workspace and the core, but it must not introduce personal data into the public repository.
