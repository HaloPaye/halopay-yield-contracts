# Contributing to HaloPay

We welcome contributions! Please adhere to the following strict guidelines:

## Pull Request Rules
- All PRs must target the `main` branch.
- CI must pass 100% (Rust tests, Pytest, Linting).
- Code must align with the Domain-Driven Design (DDD) architecture.

## Conventional Commits
Use conventional commits for your PR titles and commit messages:
- `feat(scope): add new feature`
- `fix(scope): resolve bug`
- `docs(scope): update documentation`
- `chore(scope): repository maintenance`

## DDD Layout
- Place core contract logic in `contracts/src/core/mod.rs` (using `core_domain`).
- Place external interfaces in `contracts/src/interfaces/mod.rs`.
- Off-chain domain logic goes to `agent/src/domain/`.
- Off-chain infrastructure goes to `agent/src/infrastructure/`.
