from __future__ import annotations

from pathlib import Path

from private_os.skills import ALL_SKILLS
from private_os.skills.manifest import EXPORTABLE_SKILLS

SECRET_PATTERNS = ["sk-", "password=", "secret=", "api_key", "token="]


def validate_skill_text(text: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    if "approval" not in lowered:
        errors.append("missing approval policy")
    if "business" not in lowered:
        errors.append("missing private/business separation")
    if any(pattern in lowered for pattern in SECRET_PATTERNS):
        errors.append("contains possible secret")
    return errors


def validate_exportable_manifests() -> dict[str, list[str]]:
    by_id = {skill.manifest.id: skill.manifest for skill in ALL_SKILLS}
    result: dict[str, list[str]] = {}
    for skill_id in EXPORTABLE_SKILLS:
        manifest = by_id.get(skill_id)
        errors = []
        if manifest is None:
            errors.append("missing internal skill")
        elif not manifest.approval_requirements and skill_id not in {"decision_matrix"}:
            errors.append("missing approval requirements")
        result[skill_id] = errors
    return result


def validate_export_directory(path: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for skill_dir in path.iterdir() if path.exists() else []:
        if not skill_dir.is_dir():
            continue
        errors = []
        for filename in ["skill.yaml", "README.md", "instructions.md", "examples.md"]:
            if not (skill_dir / filename).exists():
                errors.append(f"missing {filename}")
        instructions_path = skill_dir / "instructions.md"
        if instructions_path.exists():
            errors.extend(validate_skill_text(instructions_path.read_text(encoding="utf-8")))
        result[skill_dir.name] = errors
    return result
