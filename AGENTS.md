# AGENTS.md

Questo repository contiene il core open source di `private-os`.

## Fonte primaria

Leggere e rispettare `CONSTITUTION.md` come costituzione operativa del progetto.
Questo file resta volutamente corto per ridurre contesto e costi token.

## Regole operative

- Lingua predefinita: italiano.
- Ambito: workflow personali locali, non business.
- Separare sempre dati personali e dati business.
- Non accedere a repository, credenziali o sistemi business senza richiesta esplicita.
- Non inviare email, messaggi, form, documenti o prenotazioni senza approval esplicita.
- Non salvare segreti, token, password, OTP, dati bancari o documenti sensibili completi nel repo.
- Usare safe mode, dry-run e approval queue come default.
- Tenere memoria, log, workspace e database reali solo in path locali non tracciati.
- Prima di costruire capability generiche, verificare plugin, MCP, skill o tool gia' disponibili.
- Ogni task significativa deve avere prossima azione concreta, follow-up se coinvolge terzi, e log essenziale.
- Preferire patch mirate, test focalizzati e output brevi.

## File chiave

- `CONSTITUTION.md`: costituzione operativa pubblica.
- `README.md`: setup e comandi.
- `config/`: policy, permessi, skill e costi.
- `.env.example`: esempio di configurazione locale.
- `workflows/`: workflow operativi.
- `private_os/`: implementazione Python.
- `tests/`: test del sistema.
