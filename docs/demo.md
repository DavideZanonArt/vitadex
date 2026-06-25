# Anonymous Demo

The demo command creates synthetic local data so new users can inspect the CLI and dashboard without adding personal context.

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

## Resetting the Demo

The demo writes to the configured local runtime. To start fresh, point `VITADEX_STATE_ROOT` and `VITADEX_DB_PATH` at a new temporary directory, or remove the local demo runtime after confirming it contains no personal data.
