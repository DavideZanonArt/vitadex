# Anonymous Demo

The demo command creates synthetic local data so new users can inspect the CLI and dashboard without adding personal context.

The demo is the fastest way to understand VitaDex. It shows how tasks, memory, approvals, and follow-ups fit together without using real personal data.

```bash
vitadex init
vitadex demo seed
vitadex dashboard
vitadex task list
vitadex approvals list
vitadex followups list
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
- `vitadex task list` should show `Compare two anonymous apartment options`.
- `vitadex approvals list` should show `Send anonymous availability request`.
- `vitadex followups list` should show `Check whether the demo landlord replied`.
- `vitadex web` should start the local web dashboard.
- the generated records should be synthetic and safe to inspect.
- no external email, calendar, browser, payment, or messaging action should run.

## Expected Seed Output

`vitadex demo seed` returns JSON with generated local IDs and next steps:

```json
{
  "seeded": true,
  "story": "Anonymous apartment shortlist with memory, task state, approval queue, and follow-up.",
  "task_id": "task_...",
  "memory_id": "mem_...",
  "approval_id": "appr_...",
  "followup_id": "fu_...",
  "note": "Synthetic demo data only. Safe to inspect with `vitadex dashboard` or `vitadex web`.",
  "next_steps": [
    "Run `vitadex dashboard` to see the connected local state.",
    "Run `vitadex task show <task_id>` to inspect the operational task.",
    "Run `vitadex approvals list` to see the draft-only external action.",
    "Run `vitadex followups list` to see the pending next step.",
    "Run `vitadex web` for the local read-only dashboard."
  ]
}
```

The exact IDs are generated locally and will differ on every clean runtime.

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
