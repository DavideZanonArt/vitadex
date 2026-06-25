# AGENTS.md

This repository contains the open-source core of `vitadex`.

## Primary Source

Read and follow `CONSTITUTION.md` as the project's operating constitution.
This file intentionally stays short to reduce context and token costs.

## Operating Rules

- Default language: English.
- Scope: local personal workflows, not business operations.
- Always separate personal data from business data.
- Do not access business repositories, credentials, or systems without an explicit request.
- Do not send emails, messages, forms, documents, or bookings without explicit approval.
- Do not store secrets, tokens, passwords, OTPs, banking data, or complete sensitive documents in the repo.
- Use safe mode, dry-run, and the approval queue by default.
- Keep real memory, logs, workspace data, and databases only in untracked local paths.
- Before building generic capabilities, check plugins, MCP servers, skills, or tools that already exist.
- Every significant task should have a concrete next action, a follow-up if third parties are involved, and an essential log trail.
- Prefer targeted patches, focused tests, and concise output.

## Key Files

- `CONSTITUTION.md`: public operating constitution.
- `README.md`: setup and commands.
- `config/`: policies, permissions, skills, and costs.
- `.env.example`: local configuration example.
- `workflows/`: operating workflows.
- `vitadex/`: Python implementation.
- `tests/`: system tests.
