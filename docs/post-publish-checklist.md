# Post Publish Checklist

## GitHub

- abilita branch protection su `main`
- richiedi PR per modifiche a `main`
- rendi obbligatorie le Actions verdi
- abilita `Dependabot alerts`
- abilita `Dependabot security updates`
- abilita `Secret scanning` se disponibile

## Repository Hygiene

- controlla regolarmente `.secrets.baseline`
- aggiorna `CHANGELOG.md` ad ogni release
- mantieni `README.md` allineato al setup reale
- rimuovi esempi che diventano troppo vicini a casi reali

## Local Runtime

- usa solo `.env.local`
- usa solo `CONSTITUTION.local.md`
- mantieni `PRIVATE_OS_STATE_ROOT` fuori dal repository
- non fare commit di memoria, DB, log o workspace

## Release

- tagga la release
- scrivi release notes sintetiche
- verifica CI verde prima del tag
