# Codex Local Workflow

This document describes the recommended setup for using `vitadex` as the public core and Codex as a local agent on top of an untracked personal overlay.

## Goal

- clean public repository
- personal data only on this computer
- Codex attached to the local clone of the repository
- runtime and memory outside version control

## Recommended Structure

- local clone of the `vitadex` repository
- `.env.local` untracked inside the clone
- `CONSTITUTION.local.md` in `VITADEX_STATE_ROOT`
- memory, database, logs, and workspace in `~/.vitadex/`

## Bootstrap

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
./scripts/bootstrap-local.sh
vitadex init
```

## How Codex Works

Codex operates on the local clone of the repository and can:

- read the public core
- modify public code
- use `.env.local`
- use local runtime data

Codex must not:

- commit personal data
- move real memory into the repository
- create public examples from real data

## Recommended Flow

1. update the local clone of the public core
2. leave the local overlay unchanged
3. use Codex on the local clone
4. verify that every publishable change does not touch personal runtime data
5. commit only public code and documentation
