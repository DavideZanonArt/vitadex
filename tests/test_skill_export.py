from __future__ import annotations

from typer.testing import CliRunner

from private_os.cli import app
from private_os.skills.exporter import SkillExporter
from private_os.skills.validator import validate_export_directory, validate_exportable_manifests


def test_skills_validate():
    result = validate_exportable_manifests()
    assert result["housing_search"] == []
    assert result["quote_request"] == []


def test_export_creates_expected_directory_structure(tmp_path):
    exported = SkillExporter(tmp_path).export("housing_search")
    skill_dir = exported[0]

    assert skill_dir.name == "private-os-housing-search"
    assert (skill_dir / "skill.yaml").exists()
    assert (skill_dir / "README.md").exists()
    assert (skill_dir / "instructions.md").exists()
    assert (skill_dir / "examples.md").exists()
    assert (skill_dir / "bin" / "housing-search").exists()


def test_exported_instructions_include_approval_policy(tmp_path):
    skill_dir = SkillExporter(tmp_path).export("housing_search")[0]
    instructions = (skill_dir / "instructions.md").read_text(encoding="utf-8")

    assert "Approval policy" in instructions
    assert "Create private-os approval objects" in instructions
    assert "Do not access business systems" in instructions


def test_no_secrets_are_exported(tmp_path):
    SkillExporter(tmp_path).export()
    validation = validate_export_directory(tmp_path)

    assert validation
    assert all("contains possible secret" not in errors for errors in validation.values())


def test_skill_export_cli(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["skills", "export", "--skill", "housing_search", "--target", str(tmp_path)],
        env={"PRIVATE_OS_IGNORE_CONSTITUTION": "true"},
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "private-os-housing-search" / "skill.yaml").exists()
