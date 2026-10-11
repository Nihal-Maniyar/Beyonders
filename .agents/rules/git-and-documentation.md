# Git and Documentation Rules

## 1. Branch Strategy and Isolation
- All development and bug fixes must take place on the designated feature branch (`feature/learnloop-v1-foundation`).
- Never commit directly to `main` without explicit owner permission.
- Never push directly to `origin/main` without explicit owner authorization.
- Never use destructive Git commands (`git reset --hard`, `git clean -fd`, `git push --force`) that could discard uncommitted or historical work.

## 2. Commit Standards
- Commit messages must be structured and meaningful (Conventional Commits):
  - `feat(...)`: new functionality
  - `fix(...)`: bug fix
  - `test(...)`: test addition or update
  - `docs(...)`: documentation updates
  - `refactor(...)`: structural code improvement without behavior change
- Review `git diff` before every commit.
- Never stage or commit `.env`, `*.db`, SQLite files, or temporary build outputs.

## 3. Documentation Synchronization
- Any change to architecture, endpoints, or database tables must be reflected in the relevant docs:
  - `docs/architecture.md`: Component layout and data flow.
  - `docs/api.md`: Endpoint contracts, query parameters, payloads, status codes.
  - `docs/database.md`: Final relational schema, constraints, indexes.
  - `docs/er-diagram.mmd`: Canonical Mermaid ER diagram matching models.
  - `docs/decisions.md`: Architecture decision records with rationale.
  - `README.md`: Prerequisites, run commands, test commands, live demo runbook.

