# Future OpenClaw Integration

OpenClaw should treat `vitadex` as a local and auditable backend.

## CLI contract

- Create tasks: `vitadex task create --title ... --area ... --goal ...`
- Plan: `vitadex task plan <task_id>`
- Run dry-run: `vitadex task execute <task_id> --dry-run`
- Bind Codex: `vitadex codex bind <task_id>`
- Run Codex dry-run: `vitadex codex run <task_id> --dry-run`
- Read dashboard: `vitadex dashboard`
- Read approvals: `vitadex approvals list`

## Codex harness split

Codex owns the agent session, thread continuation, workspace changes, and delegated
skills. `vitadex` owns the task registry, memory, local profile, permissions,
approval queue, follow-ups, audit log, channel formatting, dashboard, safe mode,
and final summary. The adapter starts in `dry_run` and `fail_closed`.

## Telegram

Telegram can create tasks and show compact dashboards. It must not send external actions on behalf of the local user. Approvals must be explicit, tracked, and tied to a visible payload.

## Codex

Codex can add or improve skills, templates, and tests. It must stay inside the local `vitadex` workspace and must not use business repositories or data.

## Gmail

Gmail must create drafts. Sending requires a recorded approval. Sensitive attachments require explicit approval and sensitivity checks.
Integrations must call `ActionGateway`, not the tool adapters directly.

## Browser automation

Real navigation stays behind explicit configuration. Form filling, submit actions, bookings, and uploads are always approval-gated.

## Models

- Ollama/local model: classification, deduplication, low-risk summaries.
- OpenAI/GPT-5.5: planning and high-quality reasoning when authorized.
- OpenRouter: optional fallback, never mandatory.

## Business Separation

Configurations and adapters must block production systems, business credentials, and non-private repositories. No business credential should be read or imported.
