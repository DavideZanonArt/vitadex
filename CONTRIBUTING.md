# Contributing

Grazie per voler contribuire a `private-os`.

## Regole Base

- Nessun dato personale reale nel repository.
- Nessun segreto, token, path assoluto locale o credenziale nei commit.
- Tutte le azioni esterne devono restare safe-by-default.
- Ogni cambiamento deve mantenere la separazione tra core pubblico e runtime locale.

## Setup Sviluppo

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env.local
```

## Comandi Utili

```bash
pytest
ruff check .
mypy private_os
```

## Pull Request

- Mantieni le PR piccole e focalizzate.
- Aggiorna la documentazione se cambi setup, config o comportamento utente.
- Aggiungi o aggiorna test quando il rischio regressione lo giustifica.
- Conferma esplicitamente che non stai introducendo dati sensibili.

## Scope

Contributi benvenuti:

- hardening del runtime locale
- integrazioni safe-by-default
- docs
- test
- miglioramenti UX della CLI e dashboard

Contributi fuori scope senza discussione preliminare:

- bypass delle approval
- automazione di pagamenti, firme o impegni legali
- accesso a contesti business o sistemi produttivi
