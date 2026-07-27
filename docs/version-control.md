# RetainIQ — Version Control Strategy

## Overview

RetainIQ uses Git with a two-branch base model (`main`, `development`) plus
short-lived feature branches for individual units of work. This document
describes the branching model, commit conventions, and tagging/release
strategy used throughout the project, and explains why each choice was made.

---

## Branch structure

| Branch | Purpose |
|---|---|
| `main` | Stable, milestone-tagged history. Only receives merges from `development` at clean, verified checkpoints (e.g., end of a project week). Never committed to directly. |
| `development` | Integration branch. Feature branches merge here first. Represents the current working state of the project between milestones. |
| `feature/<name>` | Short-lived branches for a single unit of work (e.g., `feature/core-risk-logic`, `feature/week4-mvp-dashboard`, `feature/week5-integration`). Branched from `development`, merged back into `development` via pull request, then deleted. |

This model was chosen deliberately over committing directly to a single
branch:
- It keeps `main` always in a demonstrable, working state — useful for
  instructor review at any point without needing to check out a specific
  commit.
- It isolates in-progress or exploratory work (a feature branch) from stable
  work, so a mistake in an active feature doesn't affect anything already
  verified.
- It maps cleanly onto the project's weekly assignment structure — each
  week's scope of work lives on its own feature branch and lands as one
  reviewable, mergeable unit.

---

## Commit conventions

Commits follow a lightweight Conventional Commits style:

```
<type>: <description>
```

Common types used in this project:
- `feat:` — new functionality (e.g., `feat: add rule-based risk engine, replace hardcoded risk levels`)
- `test:` — test additions or changes (e.g., `test: add pytest unit + integration coverage for risk engine and API`)
- `refactor:` — restructuring without changing external behavior (e.g., `refactor: read student data from Postgres instead of in-memory mock list`)
- `chore:` — tooling, config, or housekeeping (e.g., `chore: add requirements.txt, request-timing middleware, split test folders`)
- `docs:` — documentation additions or changes

**Commit granularity:** Work is committed incrementally, one meaningful step
at a time, rather than batched into a single commit at the end of a work
session. Each commit should represent a state where the project still runs
(or, for test-only commits, still passes). This keeps `git log` useful as an
actual record of how the system was built, and makes it possible to
isolate exactly when a specific change was introduced if something needs to
be traced back later.

---

## Pull requests and merging

- All feature work is merged into `development` via pull request, not
  direct push, even in a single-developer context — this keeps the PR
  description as a natural checkpoint summarizing what a batch of commits
  accomplished.
- Merges preserve full commit history (standard merge or rebase-and-merge).
  **Squash merges are deliberately avoided**, since collapsing a feature
  branch's incremental commits into one would erase the step-by-step record
  described above and defeat the purpose of committing incrementally in the
  first place.
- `development` is merged into `main` only at a verified, stable point —
  typically once a week's scope is complete and tested.

---

## Tagging and releases

Annotated Git tags (`git tag -a`, not lightweight tags) mark major project
milestones, each corresponding to a completed phase of work:

| Tag | Milestone |
|---|---|
| `v0.1-architecture` | System architecture and design phase |
| `v0.2-scaffold` | Repository and project scaffolding |
| `v0.3-mock-mvp` | Initial mock-data MVP (dashboard + simulated API) |
| `v0.4-core-logic-tests` | Real rule-based risk logic, backend/frontend unit testing, output validation |
| `v0.5-integration` | Full system integration: PostgreSQL persistence, Docker containerization, performance benchmarking |

Annotated tags are used over lightweight tags because they carry a message
and author metadata, making them distinguishable from ordinary commits in
`git log` and giving each milestone a clear, documented reason for existing.

Each tag has a corresponding **GitHub Release**, with release notes
summarizing what shipped in that milestone — written from the actual commit
and PR history rather than added retroactively from memory, so the notes
stay factually accurate to what the code actually does at that point.

---

## Why this supports project monitoring and management

- **Traceability:** Because commits are incremental and typed
  (`feat`/`test`/`refactor`/`chore`), the history itself documents *what*
  changed and *why*, without needing a separate change log.
- **Checkpointing:** Tags and releases give fixed, citable reference points
  — useful both for grading (pointing to exactly what existed at the end of
  a given week) and for the developer's own ability to compare current state
  against a known-good prior point.
- **Isolation of risk:** Feature branches mean in-progress or experimental
  work never destabilizes `main`, so `main` can always be treated as the
  current, demonstrable state of the project.
- **Review discipline:** Routing all merges through pull requests, even
  solo, creates a natural point to re-check a batch of work before it
  becomes part of the permanent record on `development` or `main`.
