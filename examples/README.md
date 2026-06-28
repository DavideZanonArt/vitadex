# Examples

This directory contains anonymous fixtures and outputs for inspecting VitaDex without using real personal data.

## Rules

- Use synthetic people, organizations, dates, addresses, domains, and accounts.
- Do not copy private runtime files into examples.
- Do not include real emails, phone numbers, addresses, contracts, invoices, logs, or personal memory.
- Keep examples dry-run friendly and approval-first.

## What To Inspect

- `tasks/`: synthetic operational tasks.
- `plans/`: example plans generated from anonymous workflows.
- `approvals/`: draft-only external actions waiting for review.
- `followups/`: pending next steps connected to synthetic tasks.
- `outputs/`: example recommendations or summaries.
- `assets/`: generic asset tracking fixtures.

## Demo Flow

For the fastest product tour, run:

```bash
vitadex init
vitadex demo seed
vitadex dashboard
vitadex approvals list
vitadex followups list
```

The seeded demo shows how VitaDex connects memory, task state, an approval queue, and a follow-up without performing external actions.

## Contribution Checklist

Before adding an example:

- [ ] The example is synthetic.
- [ ] The example does not identify a real person or private situation.
- [ ] The example can be understood without private local context.
- [ ] Any external action is draft-only or approval-first.
- [ ] The example supports the public-core/private-runtime boundary.
