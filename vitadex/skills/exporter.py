from __future__ import annotations

from pathlib import Path

from vitadex.skills import ALL_SKILLS
from vitadex.skills.manifest import (
    EXPORTABLE_SKILLS,
    examples,
    export_name,
    instructions,
    readme,
    skill_yaml,
    wrapper_name,
    write_wrapper,
)
from vitadex.skills.validator import validate_skill_text


class SkillExporter:
    def __init__(self, target: Path):
        self.target = target.expanduser()

    def export(self, skill_id: str | None = None) -> list[Path]:
        exported: list[Path] = []
        selected = [skill for skill in ALL_SKILLS if skill.manifest.id in EXPORTABLE_SKILLS]
        if skill_id:
            selected = [skill for skill in selected if skill.manifest.id == skill_id]
        for skill in selected:
            exported.append(self._export_one(skill.manifest))
        return exported

    def _export_one(self, manifest) -> Path:
        directory = self.target / export_name(manifest.id)
        directory.mkdir(parents=True, exist_ok=True)
        files = {
            "skill.yaml": skill_yaml(manifest),
            "README.md": readme(manifest),
            "instructions.md": instructions(manifest),
            "examples.md": examples(manifest),
        }
        for filename, text in files.items():
            errors = validate_skill_text(text) if filename == "instructions.md" else []
            if errors:
                raise ValueError(f"{manifest.id}: {errors}")
            (directory / filename).write_text(text, encoding="utf-8")
        write_wrapper(directory / "bin" / wrapper_name(manifest.id), manifest.id)
        return directory
