# Anonymous Demo

The demo command creates synthetic local data so new users can inspect the CLI and dashboard without adding personal context.

The demo is the fastest way to understand VitaDex. It shows how tasks, memory, approvals, and follow-ups fit together without using real personal data.

```bash
vitadex init
vitadex demo seed
vitadex dashboard
vitadex web
```

The seed creates:

- one task about comparing anonymous apartment options
- one public memory preference
- one draft-only approval
- one follow-up

The data is intentionally generic. It should not be replaced with real user examples in the public repository.

## Expected Result

After seeding the demo:

- `vitadex dashboard` should show local operational state.
- `vitadex web` should start the local web dashboard.
- the generated records should be synthetic and safe to inspect.
- no external email, calendar, browser, payment, or messaging action should run.

## Troubleshooting

### Python Version

VitaDex requires Python 3.12 or newer:

```bash
python3.12 --version
```

If `python3.12` is not available, install Python 3.12+ for your operating system and recreate the virtual environment.

### Editable Install

Run the demo from an editable development install:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Local Runtime Paths

If the demo appears to reuse old data, point the runtime at a fresh local directory by setting the environment variables documented in `.env.example`.

Do not use real memory, real tasks, secrets, or sensitive local paths while preparing public screenshots or issues.

## Resetting the Demo

The demo writes to the configured local runtime. To start fresh, point `VITADEX_STATE_ROOT` and `VITADEX_DB_PATH` at a new temporary directory, or remove the local demo runtime after confirming it contains no personal data.
