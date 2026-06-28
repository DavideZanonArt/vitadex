# Early Feedback

VitaDex is in an early open-source stage. The most useful feedback is concrete, reproducible, and safe to share publicly.

## Where To Give Feedback

- Use GitHub Discussions for product questions, positioning feedback, and workflow ideas.
- Use GitHub Issues for reproducible bugs or well-scoped implementation work.
- Use Pull Requests for focused changes that preserve the public-core/private-runtime boundary.

Start here:

- Discussion: [What should a local-first personal OS for Codex remember?](https://github.com/DavideZanonArt/vitadex/discussions/10)
- Issues: [open issues](https://github.com/DavideZanonArt/vitadex/issues)

## Useful Feedback Questions

- Is the product promise clear in the first minute?
- Does the anonymous demo explain why VitaDex exists?
- Which concept is confusing: memory, task, approval, workflow, or follow-up?
- Which setup step feels unnecessary or fragile?
- Would you use this with Codex or another agentic coding tool?
- What should require explicit human approval?
- What should never be stored in VitaDex?

## Demo Feedback

Before giving demo feedback, try:

```bash
vitadex init
vitadex demo seed
vitadex dashboard
vitadex approvals list
vitadex followups list
```

Good demo feedback includes:

- operating system and Python version
- install command used
- command that failed, if any
- expected result
- actual result
- whether the public-vs-local boundary was clear

## Privacy Rules

Do not include:

- real personal data
- secrets, tokens, passwords, or API keys
- real emails, addresses, phone numbers, account numbers, or invoices
- complete sensitive documents
- private local paths or screenshots showing private folders
- real memory, logs, tasks, or runtime data

Use synthetic examples when explaining a workflow.

## What We Are Looking For

High-signal early feedback:

- "I expected memory to mean X, but the demo showed Y."
- "The approval queue makes sense, but I could not find the pending approval."
- "The setup failed at this command on this OS."
- "This workflow would be useful if it stayed draft-only."
- "This feature request would weaken the safety model because..."

Low-signal feedback:

- generic AI assistant feature requests
- requests for unsafe autonomous external action
- examples that require private user data
- broad rewrites without a concrete workflow
