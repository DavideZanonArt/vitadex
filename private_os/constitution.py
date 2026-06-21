from __future__ import annotations

from pathlib import Path


class ConstitutionMissingError(RuntimeError):
    pass


class Constitution:
    def __init__(self, root: Path, state_root: Path | None = None):
        self.root = root.resolve()
        self.state_root = (state_root or root).resolve()
        self.public_path = self.root / "CONSTITUTION.md"
        self.local_path = self.state_root / "CONSTITUTION.local.md"

    @property
    def path(self) -> Path:
        if self.local_path.exists():
            return self.local_path
        return self.public_path

    def exists(self) -> bool:
        return self.path.exists()

    def load(self) -> str:
        if not self.exists():
            raise ConstitutionMissingError("CONSTITUTION.md mancante: esecuzione bloccata.")
        return self.path.read_text(encoding="utf-8")

    def check(self) -> dict[str, object]:
        if not self.exists():
            return {"ok": False, "path": str(self.path), "message": "CONSTITUTION.md mancante."}
        text = self.load()
        required = [
            "Identity",
            "Mission",
            "Operating Principles",
            "Autonomy Levels",
            "Forbidden Actions",
            "Memory Policy",
            "Task Policy",
            "Communication Style",
            "Skill Policy",
            "Improvement Loop",
        ]
        missing = [item for item in required if item not in text]
        return {"ok": not missing, "path": str(self.path), "missing_sections": missing}

    def risky_action_context(self) -> list[str]:
        return [
            "CONSTITUTION.md §3: Ask approval before external actions.",
            "CONSTITUTION.md §5: Forbidden actions include payments, signatures, legal commitments, "
            "sensitive documents, business systems, secrets, and unapproved messages.",
            "CONSTITUTION.md §8: Italian, direct, clear, no fake certainty.",
        ]

    def update_proposal(self) -> str:
        return (
            "# Proposta aggiornamento CONSTITUTION.md\n\n"
            "## Motivo\n\n"
            "- Descrivere il problema operativo osservato.\n\n"
            "## Modifica proposta\n\n"
            "- Sezione da aggiornare:\n"
            "- Testo proposto:\n\n"
            "## Impatto sicurezza/privacy\n\n"
            "- Nessun rilassamento dei divieti senza revisione esplicita.\n"
        )
