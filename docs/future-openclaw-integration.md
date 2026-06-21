# Future OpenClaw Integration

OpenClaw dovrebbe trattare `private-os` come backend locale e auditable.

## CLI contract

- Creare task: `private-os task create --title ... --area ... --goal ...`
- Pianificare: `private-os task plan <task_id>`
- Eseguire dry-run: `private-os task execute <task_id> --dry-run`
- Collegare Codex: `private-os codex bind <task_id>`
- Eseguire Codex dry-run: `private-os codex run <task_id> --dry-run`
- Leggere dashboard: `private-os dashboard`
- Leggere approvazioni: `private-os approvals list`

## Codex harness split

Codex possiede sessione agente, continuazione thread, modifiche workspace e skill
delegate. `private-os` possiede registry task, memoria, profilo locale,
permission, approval queue, follow-up, audit log, formattazione canali, dashboard,
safe mode e sintesi finale. L'adapter parte in `dry_run` e `fail_closed`.

## Telegram

Telegram può creare task e mostrare dashboard sintetiche. Non deve inviare azioni esterne al posto dell'utente locale. Le approvazioni devono essere esplicite, tracciate e riferite a un payload visibile.

## Codex

Codex può aggiungere o migliorare skill, template e test. Deve rimanere nel workspace locale di `private-os` e non usare repository o dati business.

## Gmail

Gmail deve creare bozze. L'invio richiede approvazione registrata. Allegati sensibili richiedono approvazione esplicita e controllo sensibilità.
Le integrazioni devono chiamare `ActionGateway`, non direttamente i tool adapter.

## Browser automation

La navigazione reale resta dietro configurazione esplicita. Compilazione form, submit, prenotazioni e upload sono sempre approval-gated.

## Modelli

- Ollama/local model: classificazione, deduplica, riassunti low-risk.
- OpenAI/GPT-5.5: pianificazione e ragionamento di qualità quando autorizzato.
- OpenRouter: fallback opzionale, mai obbligatorio.

## Separazione business

Configurazioni e adapter devono bloccare sistemi produttivi, credenziali business e repository non privati. Nessuna credenziale business deve essere letta o importata.
