# AGENTS.md

## Repo

`omnivia-core`

## Role

Public core, graph, memory, contracts, schemas and public docs.

## Foundational principle

Prefer the simplest viable approach.

Choose fewer concepts, fewer moving parts, clearer ownership and easier verification unless complexity is clearly justified.

## Operating model

Codex is the PM, orchestrator, reviewer and integration controller.

Claude is the implementation agent.

For coding tasks:

**Claude builds. Codex manages.**

## Naming rule

Use short names by default:

- Apps
- Dev
- Pro
- Core
- Platform
- Cloud

Use **Module** for installable product sets such as Apps, Dev and Pro.

Use **Component** for reusable parts inside Apps.

Do not use deprecated terms unless quoting old docs.

## This repo owns

- graph primitives
- memory/context primitives
- public contracts
- manifest schemas
- provenance primitives

## This repo does not own

- desktop shell
- licensing
- Harness implementation
- paid Modules

## Shared OmniVia vocabulary

- Module: installable product set such as Apps, Dev or Pro.
- Apps: Module for creating and running custom business Apps.
- Dev: Module for developer tools.
- Pro: Module for premium local features.
- App: custom hosted business application.
- Component: reusable part inside an App.
- Harness: controlled runtime boundary.
- Module Manifest: definition file for an installable Module.

## Deprecated terms

Avoid unless quoting old docs:

- Extension
- Capability
- Pack
- Add-on
- Layer
- Space
- Surface
- Graph App
- Brick
- Block
- Studio

## Repo boundary rules

- Do not make changes outside this repo unless Codex explicitly created a cross-repo integration task.
- Do not add paid Module implementation code to the base platform.
- Do not bypass Harness APIs.
- Do not access connector credentials directly.
- If the task requires another repo, stop and report the required cross-repo change.

## Required PM context

Read the operating model in:

`/Users/claytonread/Projects/omnivia-pm/docs/operating-model/codex-claude-multirepo-workflow.md`

Use the Claude implementation task template in:

`/Users/claytonread/Projects/omnivia-pm/prompts/claude-implementation-task-template.md`
