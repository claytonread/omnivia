# OmniVia Core

OmniVia Core is the public foundation for OmniVia's local-first knowledge model.

It contains public source-library primitives for representing, storing, linking,
importing, exporting, and searching local knowledge. It is intentionally not the
OmniVia desktop app, commercial platform, Dev Pack, or cloud product.

## Scope

OmniVia Core may contain:

- domain models
- file-format primitives
- graph and storage primitives
- local knowledge primitives
- backlink/link primitives
- import/export primitives
- basic search primitives
- public tests for core primitives
- public documentation that is safe for community use

OmniVia Core must not contain:

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
- private strategy, planning, prompts, or operating files
- secrets, credentials, local databases, generated builds, caches, or dependency folders

## Repository Split

OmniVia uses a split repository model:

| Repository | Visibility | Purpose |
|---|---|---|
| `omnivia-core` | Public | Core primitives and public documentation. |
| `omnivia-platform` | Private | Base app, runtime, UI, desktop shell, distribution, module loader, licensing and entitlement client boundaries. |
| `omnivia-dev-pack` | Private | Optional downloadable Dev module with MCP, CLI, repo indexing, code graph, and agent context pack features. |
| `omnivia-cloud` | Private | Future cloud implementation placeholder. |
| `omnivia-pm` | Private | Planning, ADRs, roadmap, task backlog, strategy, prompts, reviews, and repository governance. |

Dependency direction flows from private implementation repositories toward this
public core. `omnivia-core` must not depend on private repositories.

## Status

This repository is being reduced to public core only. App/runtime and Dev-specific
code have been moved or assigned to private repositories.
