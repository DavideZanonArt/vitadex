# Glossary

This glossary defines the public-safe terms used across VitaDex docs and issues.

## Public Core

The versioned open-source repository: code, tests, documentation, base configuration, templates, and anonymous examples.

The public core must not contain real personal data, secrets, private logs, private memory, or sensitive local paths.

## Private Runtime

The untracked local state used by a VitaDex user: real memory, tasks, logs, workspace files, local overrides, and the SQLite database.

The private runtime should live outside version control.

## Memory

Structured local context that can help future work: preferences, decisions, facts, constraints, or review notes.

Memory is not a replacement for source control, secrets management, or complete sensitive documents.

## Task

An operational work item with status, goal, assumptions, constraints, next actions, and relevant context.

Tasks give Codex and other tools durable state outside a chat session.

## Workflow

A documented process for a repeatable personal operation, such as requesting a document, comparing purchase options, planning travel, or preparing a follow-up.

Public workflows must use synthetic examples.

## Approval

A review item for an external or sensitive action.

VitaDex should draft and track actions that need human review instead of silently executing them.

## Follow-Up

A reminder or pending next step linked to a task, workflow, approval, or external dependency.

Follow-ups keep work from disappearing after a single agent session.

## Dry Run

A safe execution mode that plans or drafts an action without performing the external action.

Dry-run behavior is the default expectation for integrations that could affect the outside world.

## Fail Closed

A safety posture where the system refuses or stops when it is missing required configuration, permission, or approval.

Fail-closed behavior is preferred over guessing.

## Synthetic Demo Data

Anonymous example data created for demos, tests, screenshots, and documentation.

Synthetic data must not be traceable to real people, accounts, private tasks, private documents, or local runtime state.
