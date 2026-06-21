# Post Publish Checklist

## GitHub

- enable branch protection on `main`
- require PRs for changes to `main`
- make passing Actions mandatory
- enable `Dependabot alerts`
- enable `Dependabot security updates`
- enable `Secret scanning` when available

## Repository Hygiene

- review `.secrets.baseline` regularly
- update `CHANGELOG.md` for every release
- keep `README.md` aligned with the real setup
- remove examples that become too close to real cases

## Local Runtime

- use only `.env.local`
- use only `CONSTITUTION.local.md`
- keep `PRIVATE_OS_STATE_ROOT` outside the repository
- do not commit memory, the database, logs, or workspace files

## Release

- tag the release
- write concise release notes
- verify CI is green before tagging
