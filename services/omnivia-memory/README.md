# OmniVia Core Memory Primitives

This package contains public OmniVia Core primitives for local-first knowledge
memory, persistence, provenance, workspace modeling, ingestion, graph
relationships, and basic search.

It intentionally does not include OmniVia Dev Pack interfaces such as MCP, Dev
CLI workflows, repo indexing, code graph features, or agent context packs. Those
belong in the private `omnivia-dev-pack` repository.

It also does not include the desktop runtime, app shell, local HTTP runtime
adapter, UI bridge, entitlement client, or distribution logic. Those belong in
the private `omnivia-platform` repository.

## Included Areas

- memory models and service logic
- lifecycle and provenance primitives
- workspace models and persistence
- local ingestion primitives
- graph entity and relationship primitives
- basic graph/search services
- focused public core tests

## Repository Boundary

Keep this package public-safe. Do not add:

- MCP server code
- Dev CLI code
- agent context pack generation
- repo indexing or code graph features
- Electron, Tauri, preload, renderer, or runtime adapter code
- licensing, entitlement, billing, account, or cloud implementation
- private planning, operating, prompt, or strategy material
