# Architecture

## Modello

`private-os` usa una separazione netta tra:

- core pubblico versionato
- runtime locale non tracciato

## Core Pubblico

Il core contiene:

- codice Python
- test
- documentazione
- config base
- esempi anonimi

## Runtime Locale

Il runtime contiene:

- memoria reale
- task reali
- log
- workspace
- database SQLite
- override locali

## Flusso Operativo

1. un input crea o aggiorna una task
2. il sistema recupera memoria rilevante
3. seleziona una skill
4. produce un piano
5. esegue solo in `dry_run` se l'azione è esterna
6. genera approval e follow-up
7. registra audit log

## Integrazione Codex

Codex lavora sul workspace locale e sul core, ma non deve introdurre dati personali nel repository pubblico.
