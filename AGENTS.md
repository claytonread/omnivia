# AGENTS.md

## Purpose

This repository is `omnivia-core`, the public OmniVia core repository.

It should contain only public, source-library core primitives for OmniVia:

- domain models
- file-format primitives
- graph and storage primitives
- local knowledge primitives
- backlink/link primitives
- import/export primitives
- basic search primitives
- public tests for core primitives
- public documentation that is safe for community use

## Repository Boundary

Do not add the following to this repository:

- desktop app code
- runtime adapter code
- UI/interface code
- Electron or Tauri code
- app shell, preload, main, or renderer bridge code
- licensing, entitlement, or billing implementation
- MCP server implementation
- Dev CLI implementation
- repo indexing, code graph, or agent context pack features
- cloud services or cloud client code
- private strategy, roadmap, planning, prompts, or operating files
- Claude/Codex private workflow files
- secrets, credentials, local databases, generated builds, caches, or dependency folders

## Related Private Repositories

- `omnivia-platform`: private base app and commercial platform.
- `omnivia-dev-pack`: private optional downloadable Dev module.
- `omnivia-cloud`: private future cloud placeholder.
- `omnivia-pm`: private planning, operating, ADR, roadmap, task, prompt, and governance repository.

## Dependency Direction

`omnivia-core` must not depend on private repositories.

Private repositories may consume or extend `omnivia-core`, but this repository must remain usable as the public foundation.

## Contribution Rules

Keep changes small, public-safe, and focused on reusable core primitives.

Before committing:

1. Check `git status`.
2. Review the diff.
3. Confirm no private planning or operating material is included.
4. Confirm no secrets, local databases, generated files, or dependency folders are included.
5. Run relevant package-specific checks where available.
