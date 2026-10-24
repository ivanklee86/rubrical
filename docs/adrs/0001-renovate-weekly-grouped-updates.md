# 0001: Renovate weekly grouped updates with gated automerge

**Status: accepted** (2026-10-24)

## Context

Renovate ran every two weeks with a blanket `automerge: true`, but the repo had GitHub auto-merge turned off and no
required checks, so green PRs sat waiting for the next Renovate run. CI flaked on bot PRs because
`arduino/setup-task` called the GitHub API without authentication and hit the rate limit. And Renovate classes a
Python runtime bump (3.14 → 3.15 in `.python-version`) as *minor*, so the blanket automerge could have moved the
runtime without review if CI had happened to pass.

This follows tangle's setup ([ADR 0013](https://github.com/ivanklee86/tangle/blob/main/docs/adrs/0013-renovate-weekly-grouped-updates.md),
[ADR 0016](https://github.com/ivanklee86/tangle/blob/main/docs/adrs/0016-automerge-major-updates-outside-go-and-ts.md)).
The full plan is in [`docs/agents/plans/renovate-weekly-grouped-updates.md`](../agents/plans/renovate-weekly-grouped-updates.md).

## Decision

- Renovate runs **on Fridays** with a **5-day `minimumReleaseAge`**.
- One PR per ecosystem:
  - `python`: pep621, pyenv, the Dockerfile's `dhi.io/python` and `ghcr.io/astral-sh/uv`, and the devcontainer
    Python image. These move together on a runtime bump.
  - `ci`: GitHub Actions, plus regex-tracked pins in workflows.
  - `devcontainer dependencies`
  - Weekly lock file maintenance, in its own PR.
- Everything automerges, majors included, **except Python majors** (pep621, pyenv, DHI, and the devcontainer Python
  image).
- The Python runtime is capped at `<3.15`. Moving to 3.15 is a deliberate change: it bumps `requires-python` and the
  DHI and devcontainer tags, and it waits for 3.15 wheels (for example, `cffi`). Drop the cap as part of that change.
- `main` has a ruleset that requires the `main`, `docker`, and `pre-commit` checks, and repo auto-merge is on. This
  lets Renovate's `platformAutomerge` merge as soon as CI passes.
- Renovate authenticates to `dhi.io` with a `DHI_TOKEN` secret stored in the Mend developer portal.

## Consequences

- At most a handful of Renovate PRs a week, and most merge with no one touching them.
- Python majors and the 3.15 runtime need a human.
- If the `DHI_TOKEN` stops working, the dashboard shows a `dhi.io` lookup failure again. Rotate the Docker Hub token
  in the Mend portal.
- Pins Renovate can't see on its own use the `# <datasource>/<depName>` comment convention in workflows.
