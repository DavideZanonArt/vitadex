# Local Setup

`private-os` separates the public core from local runtime data.

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
PRIVATE_OS_STATE_ROOT=~/.private-os
PRIVATE_OS_DATA_DIR=~/.private-os/data
PRIVATE_OS_MEMORY_DIR=~/.private-os/memory
PRIVATE_OS_LOG_DIR=~/.private-os/logs
PRIVATE_OS_WORKSPACE_DIR=~/.private-os/workspace
PRIVATE_OS_DB_PATH=~/.private-os/data/private_os.sqlite
```

## 4. Initialize the runtime

```bash
./scripts/bootstrap-local.sh
private-os init
```

## 5. Optional local overlay

For untracked local rules or customizations you can use:

- `CONSTITUTION.local.md`
- `.env.local`
- directory runtime sotto `PRIVATE_OS_STATE_ROOT`

These files must not be committed.

## 6. Using Codex

To use Codex on top of your local instance:

- open the local clone of the repository
- keep `.env.local` and `CONSTITUTION.local.md` out of version control
- let Codex operate only on the public core and the local runtime

Vedi anche `docs/codex-local-workflow.md`.
