# Replace Codecov with octocov and the central tracking repo

**Status: rubrical PR 1 (steps 1–4, minus the README badge) implemented. Steps 5–6 and PR 2 remain.** Open decisions resolved: octocov v0.79.0 supports `patch` in `coverage.acceptable`, so the 85% patch gate is kept (`current >= 90% && diff >= -0.5% && patch >= 85%`); `octocov dump report` confirmed repo-relative `rubrical/...` paths.

Mirror what `tangle` already ships ([tangle ADR 0010](https://github.com/ivanklee86/tangle/blob/main/docs/adrs/0010-replace-codecov-with-octocov.md),
[ADR 0011](https://github.com/ivanklee86/tangle/blob/main/docs/adrs/0011-octocov-central-reporting-and-badges-repository.md)):
octocov posts PR coverage diffs using the workflow's own `GITHUB_TOKEN` and an `artifact://` datastore, and
`ivanklee86/octocov-central` collects those artifacts daily and publishes a public badge.

rubrical is simpler than `tangle`: one test job and one coverage file, so no separate `report` job and no
coverage merging.

## How tangle does it (reference)

- `tangle` CI uploads raw coverage profiles as artifacts. A `report` job runs `k1LoW/octocov-action`
  (SHA-pinned, binary pinned to `v0.79.0`) with `actions: write` for the `artifact://${GITHUB_REPOSITORY}`
  datastore. It stores reports on `main`, and on PRs it diffs against `main` and comments.
- `octocov-central` runs octocov in central mode on a daily cron, reading `artifact://ivanklee86/tangle` with
  the `TANGLE_ARTIFACTS_TOKEN` PAT and writing `badges/<owner>/<repo>/*.svg`. Its `.octocov.yml` omits
  `central.push`, because octocov's own go-git push never authenticated, and the workflow commits and pushes
  with plain `git` instead.

## 1. Emit LCOV from pytest

In `tasks/python.yaml` `test-cov`, add (or swap the XML report for) `--cov-report lcov:test_results/cov.lcov`.

coverage.py's Cobertura XML uses an absolute `<source>` plus filenames relative to it, and octocov's path
handling for that is unverified. coverage.py's LCOV writes repo-relative `SF:rubrical/...` paths, which is the
safer choice. **Verify** with `octocov dump report` that the file paths come out repo-relative. This needs the
devcontainer, since `.venv` only works there.

## 2. Add `.octocov.yml`

```yaml
coverage:
  paths:
    - test_results/cov.lcov
  # Rough equivalent of codecov.yaml's project target 90% / threshold 0.5%.
  acceptable: current >= 90% && diff >= -0.5%
report:
  datastores:
    - artifact://${GITHUB_REPOSITORY}
  if: is_default_branch
diff:
  datastores:
    - artifact://${GITHUB_REPOSITORY}
  if: is_pull_request
comment:
  if: is_pull_request
```

Open decisions:

- `codecov.yaml` also has a **patch** gate (85% target), but I don't know of a direct octocov equivalent. Check
  the octocov docs, or accept dropping it.
- The `acceptable` expression syntax is from memory. Check it against octocov `v0.79.0`.
- `tangle` sets no gate at all, so keeping one here is a deliberate difference.

## 3. Update `.github/workflows/ci.yaml`

- Add a job-level `permissions:` block to `main`: `contents: read`, `pull-requests: write`, `actions: write`.
  The workflow has none today, so it relies on the repo's default token permissions.
- Replace `codecov/codecov-action@v6` with:

  ```yaml
  - name: Report coverage via octocov
    # SHA-pinned rather than the mutable tag: this step runs with actions: write.
    uses: k1LoW/octocov-action@a167dc0dee441b7ffc45e1b862ab55ec0d87f278 # v1.5.2
    with:
      config: .octocov.yml
      version: v0.79.0
  ```

- Keep it running only when tests pass, as Codecov does now, so a failed run never becomes the base other PRs
  diff against.
- Known limitation: on PRs from forks the token is read-only, so the comment step fails. `tangle` has the same
  problem. It matters little here because most of rubrical's PRs are same-repo Renovate branches.

## 4. Clean up in rubrical

- Delete `codecov.yaml`.
- Mention octocov in `docs/development.md`, and optionally in `docs/agents/internals.md`.
- In a **follow-up PR**, after step 5 has produced the badge: replace the Codecov badge in `README.md` with
  `https://raw.githubusercontent.com/ivanklee86/octocov-central/main/badges/ivanklee86/rubrical/coverage.svg`
  (link target: match whatever `tangle`'s README uses).

## 5. Changes in `octocov-central`

- Add `- artifact://ivanklee86/rubrical` under `central.reports.datastores` in `.octocov.yml`.
- **Manual (GitHub UI):** edit the fine-grained PAT to also grant read-only Actions access on
  `ivanklee86/rubrical`. Central mode uses a single `OCTOCOV_GITHUB_TOKEN` for every source.
- Optionally save it under a generic secret name, such as `OCTOCOV_ARTIFACTS_TOKEN`, and update
  `.github/workflows/central.yaml` to use it. `TANGLE_ARTIFACTS_TOKEN` no longer describes what it's for.
- Once rubrical's `main` has completed one CI run, trigger `central.yaml` via `workflow_dispatch` and confirm
  `badges/ivanklee86/rubrical/coverage.svg` appears.

## 6. Manual cleanup after merge

- Remove the `CODECOV_TOKEN` secret if there is one, and the Codecov app or project for rubrical.
- Codecov's historical data does not carry over.

## Order of work

1. **rubrical PR 1:** steps 1–3, plus deleting `codecov.yaml` and updating the docs. Merge to `main`.
2. **octocov-central:** step 5.
3. **rubrical PR 2:** the README badge.
4. **Optional tangle PR:** the cleanups below.

## Side findings from reviewing tangle's implementation

Minor, nothing broken:

- `docs/agents/ci.md` ("Mostly done" bullet) and workstream 11 step 6 in
  `docs/agents/plans/ci-pipeline-restructure.md` still say the badge isn't added. It is, and it renders.
- ADRs 0010 and 0011 are still `status: "proposed"`, though both are implemented.
- ADR 0011 rejects octocov.dev and plans a Pages URL, but the README badge links to `octocov.dev` and loads the
  image from `raw.githubusercontent.com`. Either update the ADR or change the link.
- `octocov-central`'s `central.yaml` uses `actions/checkout@v4` by tag and downloads the octocov tarball without
  checking its checksum, while holding a token that reaches other repos. That's a lower bar than tangle's own
  SHA-pinned CI.
