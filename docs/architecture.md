# Architecture

## Model

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

## Operational Flow

1. an input creates or updates a task
2. the system retrieves relevant memory
3. it selects a skill
4. it produces a plan
5. it executes only in `dry_run` when the action is external
6. it generates approvals and follow-ups
7. it records the audit log

## Codex Integration

Codex works on the local workspace and the core, but it must not introduce personal data into the public repository.
