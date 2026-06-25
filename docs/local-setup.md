# Local Setup

`vitadex` separates the public core from local runtime data.

## 1. Create the environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. Copy the local configuration

```bash
cp .env.example .env.local
```

## 3. Set the local paths

Use a directory outside the repository, for example:

```env
VITADEX_STATE_ROOT=~/.vitadex
VITADEX_DATA_DIR=~/.vitadex/data
VITADEX_MEMORY_DIR=~/.vitadex/memory
VITADEX_LOG_DIR=~/.vitadex/logs
VITADEX_WORKSPACE_DIR=~/.vitadex/workspace
VITADEX_DB_PATH=~/.vitadex/data/vitadex.sqlite
```

## 4. Initialize the runtime

```bash
./scripts/bootstrap-local.sh
vitadex init
```

## 5. Optional local overlay

For untracked local rules or customizations you can use:

- `CONSTITUTION.local.md`
- `.env.local`
- directory runtime sotto `VITADEX_STATE_ROOT`

These files must not be committed.

## 6. Using Codex

To use Codex on top of your local instance:

- open the local clone of the repository
- keep `.env.local` and `CONSTITUTION.local.md` out of version control
- let Codex operate only on the public core and the local runtime

Vedi anche `docs/codex-local-workflow.md`.
