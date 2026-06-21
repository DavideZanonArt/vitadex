# private-os

Framework locale-first per costruire un personal agent OS con memoria, task, piani, approvazioni, follow-up, audit log e integrazione Codex.

Il repository pubblico contiene il core del prodotto. I dati personali, la memoria reale, i log e le configurazioni dell'utente devono vivere solo in locale, fuori dal versionamento.

## Funzionalità

- Task operative con stato, obiettivo, vincoli, assunzioni e next actions.
- Memoria strutturata con review, sensibilità e ricerca locale.
- Approval queue per tutte le azioni esterne.
- Follow-up e audit log persistenti.
- Dashboard CLI e web in sola lettura.
- Skill esportabili e riusabili.
- Integrazione locale con Codex harness in modalità `dry_run` e `fail_closed`.

## Requisiti

- Python 3.12+
- ambiente locale Unix-like o macOS
- nessuna credenziale business nel repository

## Installazione

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env.local
private-os init
```

## Configurazione Locale Sicura

Il repository pubblico non deve contenere dati personali. Usa sempre un overlay locale non tracciato:

```bash
cp .env.example .env.local
```

Configura almeno questi path locali:

- `PRIVATE_OS_STATE_ROOT`
- `PRIVATE_OS_DATA_DIR`
- `PRIVATE_OS_MEMORY_DIR`
- `PRIVATE_OS_LOG_DIR`
- `PRIVATE_OS_WORKSPACE_DIR`
- `PRIVATE_OS_DB_PATH`

Esempio consigliato:

```env
PRIVATE_OS_STATE_ROOT=~/.private-os
PRIVATE_OS_DATA_DIR=~/.private-os/data
PRIVATE_OS_MEMORY_DIR=~/.private-os/memory
PRIVATE_OS_LOG_DIR=~/.private-os/logs
PRIVATE_OS_WORKSPACE_DIR=~/.private-os/workspace
PRIVATE_OS_DB_PATH=~/.private-os/data/private_os.sqlite
```

Il file `.env.local` non va committato. Lo stesso vale per `memory/`, `housing/`, `workspace/`, `logs/`, DB SQLite e qualsiasi file con contenuti personali.

## Quickstart

```bash
private-os init
private-os memory add --type preference --area travel --text "Preferisco viaggi in auto con Wi-Fi affidabile."
private-os task create --title "Preparare richiesta appartamento temporaneo" --area home --goal "Raccogliere opzioni e bozze di contatto"
private-os task plan <task_id>
private-os task execute <task_id> --dry-run
private-os approvals list
private-os dashboard
private-os web
private-os codex status
```

## Modello Di Sicurezza

Safe mode è attivo di default:

- browser in modalità mock/search-plan
- Gmail crea bozze, non invia
- Calendar crea proposte, non eventi reali
- Drive usa storage locale mock
- Telegram genera notifiche mock
- filesystem limitato all'ambito configurato
- pagamenti, firme e impegni legali sono vietati

## Modello Repository

Il pattern previsto è:

- `repo pubblico`: codice, test, documentazione, esempi anonimi, config base
- `istanza locale`: profilo utente, memoria reale, task reali, output runtime, override locali
- `Codex`: agganciato all'istanza locale, non ai dati pubblicati

## Struttura Principale

- `private_os/`: implementazione Python
- `tests/`: test automatici
- `config/`: policy e default versionati
- `docs/`: architettura, setup locale e integrazioni
- `examples/`: fixture anonime
- `templates/`: template generici
- `workflows/`: workflow documentati

## Skill Incluse

- `housing_search`
- `quote_request`
- `travel_planning`
- `appointment_booking`
- `document_request`
- `complaint_management`
- `purchase_research`
- `email_followup`
- `decision_matrix`
- `dashboard_digest`

## Integrazione Codex

`private-os codex ...` collega una task locale a un thread Codex. Il core mantiene task, memoria, approvals, follow-up e audit log; Codex mantiene la sessione agente e le modifiche workspace.

Vedi `docs/future-openclaw-integration.md` e `private_os/integrations/codex_harness/README.md`.

## Sviluppo

```bash
pytest
ruff check .
mypy private_os
```

Per aggiungere una skill:

1. Crea `private_os/skills/<skill>.py`.
2. Estendi `Skill`.
3. Definisci `manifest`.
4. Implementa `plan()` ed `execute()`.
5. Registra la skill in `private_os/skills/__init__.py`.
6. Aggiungi workflow, template e test.

## Contributi

Apri issue o pull request seguendo `CONTRIBUTING.md`. Le PR non devono contenere dati personali, segreti, path locali assoluti o esempi reali riconducibili a persone reali.

## Licenza

Vedi `LICENSE`.
