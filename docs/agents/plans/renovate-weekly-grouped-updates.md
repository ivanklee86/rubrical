# Renovate: weekly grouped updates with gated automerge

**Status: implemented** (see [ADR 0001](../../adrs/0001-renovate-weekly-grouped-updates.md)). The config below
is the proposal; `renovate.json` is the source of truth, and it adds a Task version pin and an `extractVersion` rule.

Mirror what `tangle` already ships ([tangle ADR 0013](https://github.com/ivanklee86/tangle/blob/main/docs/adrs/0013-renovate-weekly-grouped-updates.md),
[ADR 0016](https://github.com/ivanklee86/tangle/blob/main/docs/adrs/0016-automerge-major-updates-outside-go-and-ts.md)):
a weekly schedule, one PR per ecosystem, a 5-day `minimumReleaseAge`, and automerge for everything except
majors in the primary language.

## How tangle does it (reference)

- `"schedule": ["on friday"]`, `minimumReleaseAge: "5 days"` with `minimumReleaseAgeBehaviour: "timestamp-optional"`.
- Ecosystem groups (`go`, `ts`, `k8s`, `ci`) built from `matchDatasources`/`matchManagers`, with each language's
  Dockerfile base images (`golang`, `node`) pulled into the same group by `matchPackageNames`.
- Automerge for `minor`/`patch`/`pin`/`digest` everywhere, and for majors everywhere *except* Go and TypeScript
  (ADR 0016).
- Version caps with a `description` saying when to drop them (`typescript` `<7`).
- `customManagers` regex entries for pins Renovate can't otherwise see.
- `renovate-config-validator` in pre-commit (rubrical already has this).

## Why rubrical's PRs pile up

There are only three Renovate PRs open right now (#523, #532, #541), but none of them will merge on its own:

| PR | Update | State | Cause |
| --- | --- | --- | --- |
| #523 | `docker/metadata-action` v5 → v6 | all green, not merged | repo has `allow_auto_merge: false` and `main` has no branch protection, so `platformAutomerge` can't do anything. Renovate falls back to merging the PR itself on a later run, and with a biweekly schedule that run is a long way off. |
| #532 | `actions/setup-python` v6 → v7 | `main` fails | `arduino/setup-task` hit the **unauthenticated** GitHub API rate limit. This is a flake, not a v7 break. |
| #541 | Python 3.14 → 3.15 (`.python-version`) | `main` + `docker` fail | `cffi==2.0.0` has no 3.15 wheel and the DHI image has no `cc`. Renovate calls this a *minor* bump, so if CI had passed, today's blanket `automerge: true` would have moved the runtime with nobody looking. |

Two other problems:

- The Dependency Dashboard (#5) warns `Failed to look up docker package dhi.io/python: no-result`. Docker
  Hardened Images need auth, so the `Dockerfile` base image is never updated.
- Some pins are invisible to Renovate or float: `ghcr.io/astral-sh/uv:debian` in `Dockerfile` has no version,
  and octocov's `version: v0.79.0` in `ci.yaml` isn't tracked.

## 1. Fix CI so bot PRs can go green

Pass the workflow token to `arduino/setup-task` in `ci.yaml`, `release.yaml`, and `release-docs.yaml`:

```yaml
      - name: Install Task
        uses: arduino/setup-task@v3.0.0
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

Why the token: with no `version:` input the action defaults to `3.x`, and it lists Task's releases through the
GitHub REST API to turn that range into a real version. Without `repo-token` the call is unauthenticated, which
limits it to 60 requests/hour per IP, and GitHub-hosted runners share IPs. With the workflow token the limit is
per repo (about 1,000/hour). The token is already there in every run, Renovate branches included, and
`contents: read` is enough.

Also pin an exact Task version (`version: 3.54.0`). When the input is valid semver, `computeVersion` in the action
skips the API lookup, and the pin gives Renovate something to bump. Leave the `v` off: `semver.valid` accepts
`v3.54.0`, and the action prepends its own `v`, which gives `vv3.54.0`.

## 2. Repo settings (manual, GitHub UI)

- Turn on **Allow auto-merge** (Settings → General).
- Add a ruleset on `main` that requires the `main`, `docker`, and `pre-commit` checks. Without required checks,
  GitHub auto-merge has nothing to wait for. With them in place, `platformAutomerge` merges as soon as CI passes,
  and doesn't need another Renovate run.
- Add yourself (repo admin) as a bypass actor on the ruleset, or every change to `main` has to go through a PR
  from now on.

## 3. Restructure `renovate.json`

Groups:

- **`python`**: `pep621` (pyproject and `uv.lock`), the `pyenv` runtime (`.python-version`), the `Dockerfile`
  base images (`dhi.io/python`, `ghcr.io/astral-sh/uv`), and the devcontainer's `ghcr.io/ivanklee86/devcontainer/python`
  image. All of these must move together on a runtime bump, which is why the devcontainer image goes here and not in
  the devcontainer group.
- **`ci`**: the `github-actions` manager (this already covers `prek-version`) plus the new octocov custom manager
  (`custom.regex`).
- **`devcontainer dependencies`**: kept as it is (features only, after the python image moves out), automerged.
- Weekly `lockFileMaintenance`, so `uv.lock` picks up transitive bumps. It stays in its own
  `renovate/lock-file-maintenance` PR: Renovate doesn't merge lock file maintenance into other groups, and keeping
  it separate means a bad transitive bump can't hold up direct-dependency updates. The `>=` ranges in
  `pyproject.toml` mean most direct-dependency updates come through as lockfile-only changes too.

Python runtime cap: cap the runtime at `<3.15` (in the same style as tangle's `typescript <7` rule) until
3.15 is a deliberate change. That change also has to bump `requires-python` and the DHI and devcontainer tags,
and it waits on 3.15 wheels.

Automerge: put every non-major update on automerge, and majors too, except in the `python` group (tangle ADR 0016's
pattern applied to Python). Drop the top-level `automerge: true` and `platformAutomerge: true`: the rules now cover
automerge, and `platformAutomerge` is already Renovate's default.

A grouped branch only automerges if every update in it can automerge, so a single Python major holds the whole
`python` PR. That's intended. `separateMajorMinor` (on by default) puts majors in their own `python (major)` PR,
so the non-major `python` PR still automerges.

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "schedule": ["on friday"],
  "minimumReleaseAge": "5 days",
  "minimumReleaseAgeBehaviour": "timestamp-optional",
  "lockFileMaintenance": {
    "enabled": true,
    "schedule": ["on friday"]
  },
  "hostRules": [
    {
      "matchHost": "dhi.io",
      "username": "ivanklee86",
      "password": "{{ secrets.DHI_TOKEN }}"
    }
  ],
  "packageRules": [
    {
      "matchManagers": ["pep621", "pyenv"],
      "groupName": "python"
    },
    {
      "matchManagers": ["dockerfile"],
      "matchPackageNames": ["dhi.io/python", "ghcr.io/astral-sh/uv"],
      "groupName": "python"
    },
    {
      "matchManagers": ["devcontainer"],
      "matchPackageNames": ["ghcr.io/ivanklee86/devcontainer/python"],
      "groupName": "python"
    },
    {
      "description": "Python 3.15 is a deliberate bump (requires-python, DHI + devcontainer tags, wheels for cffi et al.); drop when moving",
      "matchPackageNames": ["python", "dhi.io/python", "ghcr.io/ivanklee86/devcontainer/python"],
      "allowedVersions": "<3.15"
    },
    {
      "matchManagers": ["github-actions", "custom.regex"],
      "groupName": "ci"
    },
    {
      "matchManagers": ["devcontainer"],
      "matchPackageNames": ["!ghcr.io/ivanklee86/devcontainer/python"],
      "groupName": "devcontainer dependencies"
    },
    {
      "matchUpdateTypes": ["minor", "patch", "pin", "digest", "lockFileMaintenance", "major"],
      "automerge": true
    },
    {
      "matchManagers": ["pep621", "pyenv"],
      "matchUpdateTypes": ["major"],
      "automerge": false
    },
    {
      "matchPackageNames": ["dhi.io/python", "ghcr.io/ivanklee86/devcontainer/python"],
      "matchUpdateTypes": ["major"],
      "automerge": false
    }
  ],
  "customManagers": [
    {
      "customType": "regex",
      "managerFilePatterns": ["/^\\.github/workflows/ci\\.yaml$/"],
      "matchStrings": ["version: (?<currentValue>v[0-9.]+) # (?<datasource>.*?)/(?<depName>.*?)\\s"]
    }
  ]
}
```

Supporting file changes:

- `ci.yaml`: annotate the octocov pin as `version: v0.79.0 # github-releases/k1LoW/octocov`, the same convention
  tangle uses for `K3D_VERSION`.
- `Dockerfile`: pin `ghcr.io/astral-sh/uv:debian` to `0.13.5-debian@sha256:…`. That's the current release, which
  `:debian` was already pulling, so behavior doesn't change. The pin gives Renovate a tag and a digest to bump.
- `ci.yaml`, `release.yaml`, `release-docs.yaml`: the exact Task `version:` from step 1, annotated
  `# github-releases/go-task/task`. The custom manager matches all workflows and accepts an optional `v`, and a
  `go-task/task` rule sets `extractVersion: "^v(?<version>.*)$"` so Renovate writes back bare versions.

## 4. Credentials for `dhi.io`

Add a `DHI_TOKEN` secret (a Docker Hub PAT with DHI pull access) for this repo in the Mend developer portal, then
use the `hostRules` entry above. If that's more than we want to maintain, use
`{"matchPackageNames": ["dhi.io/python"], "enabled": false}` instead. This makes the "manual only" choice explicit
and removes the dashboard warning. If you take that route, also take `dhi.io/python` out of the `python` group
rule, the major-automerge exclusion, and the `<3.15` cap, and drop the `hostRules` block, so no dead config is
left behind.

## 5. Clean up the existing PRs

- #523: merge now (it's green).
- #532: once step 1 lands, rebase it from the dashboard and let it automerge. It will reopen as part of the `ci` group.
- #541: close it. The `<3.15` cap stops it from coming back.
- #519 (pre-commit.ci autoupdate) isn't from Renovate, and tangle ADR 0013 deliberately leaves `rev:` bumps to
  pre-commit.ci. Look at it separately.

## Verification

- `prek run renovate-config-validator --all-files` passes.
- After the next Friday run, the Dependency Dashboard shows at most one PR each for `python`, `ci`, and
  `devcontainer dependencies` (plus `python (major)` if one is pending), and a separate lock file maintenance PR.
  It no longer shows the `dhi.io`
  lookup warning, and it lists `k1LoW/octocov` and `ghcr.io/astral-sh/uv` under detected dependencies.
- Check that a non-major `ci` PR automerges without anyone touching it once the required checks pass.

## 6. Record it as an ADR

Create `docs/adrs/` and add ADR 0001 covering the weekly grouped schedule, the `<3.15` runtime cap, and keeping
Python majors out of automerge. Tangle recorded this as ADR 0013 plus 0016. Without an ADR, the cap and the
exclusion look arbitrary to the next reader.

## Resolved questions

- Lock file maintenance gets its own PR (see step 3).
- Yes, add an ADR (step 6).
