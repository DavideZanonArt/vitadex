# Local Setup

`private-os` separa il core pubblico dai dati runtime locali.

## 1. Crea l'ambiente

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. Duplica la configurazione locale

```bash
cp .env.example .env.local
```

## 3. Imposta i path locali

Usa una directory fuori dal repository, per esempio:

```env
PRIVATE_OS_STATE_ROOT=~/.private-os
PRIVATE_OS_DATA_DIR=~/.private-os/data
PRIVATE_OS_MEMORY_DIR=~/.private-os/memory
PRIVATE_OS_LOG_DIR=~/.private-os/logs
PRIVATE_OS_WORKSPACE_DIR=~/.private-os/workspace
PRIVATE_OS_DB_PATH=~/.private-os/data/private_os.sqlite
```

## 4. Inizializza il runtime

```bash
private-os init
```

## 5. Overlay locale opzionale

Per regole o personalizzazioni locali non tracciate puoi usare:

- `CONSTITUTION.local.md`
- `.env.local`
- directory runtime sotto `PRIVATE_OS_STATE_ROOT`

Questi file non devono essere committati.
