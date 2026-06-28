from __future__ import annotations

from pathlib import Path

from vitadex.models.skill import SkillManifest

EXPORTABLE_SKILLS = {
    "housing_search": "vitadex-housing-search",
    "asset_reconciliation": "vitadex-asset-reconciliation",
    "quote_request": "vitadex-quote-request",
    "email_followup": "vitadex-email-followup",
    "decision_matrix": "vitadex-decision-matrix",
    "document_request": "vitadex-document-request",
    "travel_planning": "vitadex-travel-planning",
    "complaint_management": "vitadex-complaint-management",
}


def export_name(skill_id: str) -> str:
    return EXPORTABLE_SKILLS[skill_id]


def wrapper_name(skill_id: str) -> str:
    return export_name(skill_id).removeprefix("vitadex-")


def skill_yaml(manifest: SkillManifest) -> str:
    return "\n".join(
        [
            f"id: {export_name(manifest.id)}",
            f"name: {manifest.name}",
            f"description: {manifest.description}",
            f"area: {manifest.area}",
            f"max_autonomy_level: {manifest.max_autonomy_level}",
            f"risk_level: {manifest.risk_level}",
            "private_life_only: true",
            "approval_required_for_external_actions: true",
            "forbidden:",
            "  - payments",
            "  - signatures",
            "  - legal_commitments",
            "  - sensitive_document_sharing_without_approval",
            "  - business_system_access",
            "outputs:",
            *[f"  - {item}" for item in manifest.outputs],
            "required_tools:",
            *[f"  - {item}" for item in manifest.required_tools],
            "",
        ]
    )


def readme(manifest: SkillManifest) -> str:
    return f"# {export_name(manifest.id)}\n\n{manifest.description}\n\nPrivate-life only. Safe by default.\n"


def instructions(manifest: SkillManifest) -> str:
    return "\n".join(
        [
            f"# Instructions for {export_name(manifest.id)}",
            "",
            "## When to use",
            *[f"- {item}" for item in manifest.trigger_examples],
            "",
            "## Inputs needed",
            *[f"- {item}" for item in manifest.required_inputs],
            "",
            "## Outputs to produce",
            *[f"- {item}" for item in manifest.outputs],
            "",
            "## Approval policy",
            "- Never send external messages directly.",
            "- Create vitadex approval objects instead of sending email, forms, uploads, bookings, payments, or calendar events.",
            "- External actions require explicit approval in the private OS approval queue.",
            "",
            "## Forbidden",
            "- Payments, signatures, legal commitments, contracts, medical decisions, secrets, "
            "business repositories, and sensitive document sharing without approval.",
            "",
            "## Task logs",
            "- Update vitadex task logs with assumptions, decisions, outputs, approvals, and follow-ups.",
            "- Keep output concise, deterministic, and in English for the local operator.",
            "",
            "## Separation",
            "- Use only the local personal context explicitly provided to the system.",
            "- Do not access business systems or credentials.",
            "",
        ]
    )


def examples(manifest: SkillManifest) -> str:
    lines = [f"# Examples for {export_name(manifest.id)}", ""]
    for example in manifest.test_examples or [{"input": manifest.description}]:
        lines.append(f"- Input: {example.get('input', manifest.description)}")
        lines.append("- Expected: dry-run plan, approval objects for external actions, task log update.")
    return "\n".join(lines) + "\n"


def write_wrapper(path: Path, skill_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "#!/usr/bin/env sh\n"
        f"vitadex skills show {skill_id}\n",
        encoding="utf-8",
    )
    path.chmod(0o755)
