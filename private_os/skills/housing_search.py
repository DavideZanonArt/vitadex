from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class HousingSearchSkill(Skill):
    manifest = SkillManifest(
        id="housing_search",
        name="Ricerca affitti e casa",
        description="Cerca, struttura, confronta e gestisce ricerche di affitti temporanei.",
        area="home",
        trigger_examples=["affitto", "monaco", "casa", "appartamento", "rental", "housing"],
        required_inputs=["città", "durata indicativa"],
        optional_inputs=["budget", "quartieri", "parcheggio", "Wi-Fi", "animali", "date"],
        outputs=[
            "strategia ricerca",
            "fonti da controllare",
            "tabella confronto",
            "bozza outreach",
            "follow-up",
            "shortlist",
            "raccomandazione",
        ],
        max_autonomy_level="A3",
        required_tools=["BrowserTool(mock)", "GmailTool(draft)", "FileSystemTool"],
        approval_requirements=["Invio email", "Invio documenti", "Prenotazioni o contratti"],
        risk_level="medium",
        runbook=[
            "Definire criteri minimi.",
            "Preparare fonti e query.",
            "Costruire tabella confronto.",
            "Preparare messaggi in bozza.",
            "Creare follow-up.",
            "Richiedere approvazione prima di contatti esterni.",
        ],
        test_examples=[{"input": "Cercare affitto 6 mesi a Monaco", "matches": True}],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        memories = [m.id for m in context.get("memories", [])]
        missing = [
            "budget massimo mensile",
            "date precise di ingresso/uscita",
            "numero persone",
            "requisiti parcheggio/Wi-Fi",
        ]
        assumptions = [
            "Ricerca limitata a vita privata, senza usare dati o strumenti business.",
            "Durata: 6 mesi.",
            "Zona: centro di Monaco o massimo 10 minuti in auto dal centro.",
            "Nessun contatto esterno viene inviato senza approvazione.",
        ]
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title, task.description, *task.constraints],
            relevant_memories=memories,
            assumptions=assumptions,
            missing_info=missing,
            risks=[
                "Truffe o annunci non verificati.",
                "Richieste di deposito prima della verifica.",
                "Condivisione impropria di documenti personali.",
                "Vincoli contrattuali non adatti a 6 mesi.",
            ],
            recommended_strategy=(
                "Preparare una ricerca multi-fonte in dry-run, confrontare solo annunci verificabili, "
                "creare bozze di contatto e chiedere all'utente budget e date prima dell'invio."
            ),
            steps=[
                PlanStep(
                    title="Definire criteri",
                    description="Confermare budget, date, persone, quartieri e vincoli.",
                    output="criteri",
                ),
                PlanStep(
                    title="Preparare fonti",
                    description="Impostare lista fonti: portali affitti, serviced apartments, agenzie, gruppi verificati.",
                    tool="BrowserTool(mock)",
                    output="fonti",
                ),
                PlanStep(
                    title="Tabella confronto",
                    description="Creare schema per prezzo, zona, distanza, arredato, deposito, rischi, contatto.",
                    output="tabella",
                ),
                PlanStep(
                    title="Bozza outreach",
                    description="Preparare email IT/EN senza allegati e senza dati sensibili.",
                    autonomy_level="A3",
                    requires_approval=True,
                    tool="GmailTool(draft)",
                    output="bozza email",
                ),
                PlanStep(
                    title="Follow-up",
                    description="Creare promemoria a 3 e 7 giorni per risposte landlord/agenzie.",
                    output="follow-up",
                ),
                PlanStep(
                    title="Raccomandazione",
                    description="Produrre shortlist e scelta consigliata con rischi espliciti.",
                    output="raccomandazione",
                ),
            ],
            required_skills=["housing_search", "decision_matrix", "email_followup"],
            required_tools=["BrowserTool(mock)", "GmailTool(draft)", "FileSystemTool"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Invio richiesta disponibilità affitto Monaco",
                    "description": "Inviare la bozza a proprietari o agenzie dopo revisione dell'utente.",
                    "risk_level": "medium",
                    "sensitivity_level": "personal",
                    "payload": {"template": "templates/emails/housing-request-en.md"},
                }
            ],
            expected_outputs=[
                "Strategia di ricerca",
                "Schema fonti",
                "Tabella confronto annunci",
                "Bozze email IT/EN",
                "Follow-up",
                "Shortlist",
                "Raccomandazione",
            ],
            followups=[
                {
                    "title": "Ricontattare proprietari/agenzie senza risposta",
                    "due_date": (datetime.now(UTC) + timedelta(days=3)).date().isoformat(),
                    "trigger_condition": "Nessuna risposta dopo 3 giorni",
                    "action": "Preparare follow-up email",
                    "approval_required": True,
                },
                {
                    "title": "Decisione su budget e criteri mancanti",
                    "due_date": (datetime.now(UTC) + timedelta(days=1)).date().isoformat(),
                    "trigger_condition": "Budget o date mancanti",
                    "action": "Chiedere all'utente di confermare budget/date",
                    "approval_required": False,
                },
            ],
            final_recommendation_placeholder="Raccomandare 2-3 opzioni solo dopo verifica prezzo, posizione, durata, rischio e condizioni.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "search_strategy": [
                "Query: furnished apartment Munich 6 months city center",
                "Query: temporary rental München 6 Monate möbliert Zentrum",
                "Fonti: portali affitti, serviced apartments, agenzie locali, relocation services, gruppi verificati.",
            ],
            "comparison_columns": [
                "nome",
                "url",
                "zona",
                "distanza_auto_centro_min",
                "prezzo_mese",
                "deposito",
                "arredato",
                "Wi-Fi",
                "parcheggio",
                "durata_minima",
                "documenti_richiesti",
                "rischi",
                "prossima_azione",
            ],
            "drafts": {
                "it": "Vorrei sapere se l'appartamento è disponibile per un affitto temporaneo di circa 6 mesi...",
                "en": "I would like to ask whether the apartment is available for an approximately 6-month temporary rental...",
            },
            "recommendation_next": "Confermare budget e date prima di inviare richieste.",
        }
