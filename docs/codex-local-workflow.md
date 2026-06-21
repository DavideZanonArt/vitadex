# Codex Local Workflow

Questo documento descrive il setup consigliato per usare `private-os` come core pubblico e Codex come agente locale sopra un overlay personale non tracciato.

## Obiettivo

- repository pubblico pulito
- dati personali solo su questo computer
- Codex agganciato al clone locale del repository
- runtime e memoria fuori dal versionamento

## Struttura Consigliata

- clone locale del repository `private-os`
- `.env.local` non tracciato nel clone
- `CONSTITUTION.local.md` in `PRIVATE_OS_STATE_ROOT`
- memoria, database, log e workspace in `~/.private-os/`

## Bootstrap

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
./scripts/bootstrap-local.sh
private-os init
```

## Come Lavora Codex

Codex opera sul clone locale del repository e può:

- leggere il core pubblico
- modificare il codice pubblico
- usare `.env.local`
- usare i dati runtime locali

Codex non deve:

- committare dati personali
- spostare memoria reale nel repository
- creare esempi pubblici a partire da dati reali

## Flusso Consigliato

1. aggiorna il clone locale del core pubblico
2. lascia invariato l'overlay locale
3. usa Codex sul clone locale
4. verifica che ogni modifica pubblicabile non tocchi il runtime personale
5. fai commit solo del codice e della documentazione pubblica
