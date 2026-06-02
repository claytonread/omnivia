# Baseline Governance

This document defines how OmniVia Core benchmark baselines should be created,
validated, promoted, and used for regression decisions.

## Status

Current policy status: local preflight only.

The first committed tiny baseline is useful for exercising the benchmark and
comparison workflow, but it should not be treated as a hard CI gate until a
reference baseline has been captured under this policy.

## Reference Environment

Performance baselines are only meaningful when the environment is stable enough
to compare runs.

A promotable baseline must record:

- machine model or runner type
- operating system and version
- Python version
- CPU architecture
- memory size
- storage type when known
- OmniVia Core git commit
- benchmark profile
- command used to capture the run

For local development, use `scripts/check-core-performance.sh` as a preflight
signal. For release or CI gating, capture baselines on a named reference
machine or a pinned CI runner class.

## Capture Rules

Use the smallest profile that provides useful signal for the intended decision.

- `tiny`: local smoke and workflow validation
- `small`: development regression checks
- `medium`: release or CI candidate gate after variance is understood

Before promoting a baseline:

1. Start from a clean working tree.
2. Use the visible Core checkout, not an editable install or worktree shadow.
3. Close unrelated high-load local processes when running on a workstation.
4. Run a warm-up benchmark once and discard that report.
5. Run at least five measured benchmark passes for the target profile.
6. Compare the measured passes against the candidate baseline.
7. Promote only if the median run is representative and no measured pass has
   unexplained scenario failures.

## Variance Policy

Default comparison thresholds remain:

- warning: 10% regression
- fail: 25% regression

These thresholds are for developer visibility, not automatic CI failure, until
profile-specific variance has been measured on the reference environment.

For a hard gate, define all of the following for the chosen profile:

- allowed coefficient of variation for key metrics
- number of repeated runs
- aggregation method, usually median
- whether warnings fail the gate
- scenarios excluded from gating because they are placeholders or known noisy

Until that gate policy exists, a failing local check should trigger review, not
automatic baseline replacement.

## Promotion Rules

Promote a new baseline only when one of these is true:

- a deliberate performance improvement has landed
- a benchmark scenario changed in a way that invalidates old measurements
- the reference environment changed and the old baseline is no longer comparable
- a broader profile is being introduced for a new decision point

Do not promote a baseline just because a local run failed. First determine
whether the failure is from real code behavior, environmental noise, or an
invalid baseline.

Promotion checklist:

1. Run benchmark tests.
2. Capture repeated benchmark runs according to this policy.
3. Compare the candidate against the current baseline.
4. Save the chosen baseline under `benchmarks/baselines`.
5. Document the reason for promotion in the commit message or review note.
6. Remove transient reports from `benchmarks/reports` unless they are
   intentionally retained as public evidence.

## CI Gate Readiness

Do not enable a hard CI performance gate until all conditions are true:

- the reference runner is named and stable
- repeat count and aggregation are implemented or documented in the CI workflow
- scenario exclusions are explicit
- threshold behavior is agreed for warning and fail results
- baseline promotion requires review

Recommended first gate:

- profile: `tiny`
- mode: informational only
- command: `scripts/check-core-performance.sh`
- output: uploaded report artifacts
- failure behavior: do not block merges until variance is measured
