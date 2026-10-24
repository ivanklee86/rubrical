# Harden the GitHub integration tests against shared-state failures

**Status: implemented** (2026-10-24), except step 6, which is manual. Decisions are recorded in [ADR 0002](../../adrs/0002-github-report-id.md).

## Problem

The tests that talk to GitHub (`tests/unit/reporters/test_gh.py::test_gh_report`, `::test_gh_cleanup`, `::test_gh_report_noop`, and `tests/integration/test_cli.py::test_cli_gh_report`) all read and write comments on one shared, long-lived PR, `ivanklee86/rubrical#27`. Every CI run that has `RUBRICAL_TEST_GITHUB_ACCESS_TOKEN` runs them against that PR. Renovate routinely opens or rebases several PRs within seconds of each other, so several CI runs mutate PR #27 at the same time.

### Evidence from prior runs

| Run | Started (UTC) | Failure |
|-----|---------------|---------|
| [40081234910](https://github.com/ivanklee86/rubrical/actions/runs/40081234910) | 2026-10-24 09:15:27 | `test_cli_gh_report`: `assert 2 == 1` (two Rubrical comments). Overlapped runs 40081245491 (09:15:36) and 40081274745 (09:16:03). |
| [40079708135](https://github.com/ivanklee86/rubrical/actions/runs/40079708135) | 2026-10-24 08:52:08 | `test_gh_report`: `404 Not Found` on *update an issue comment*; `test_cli_gh_report`: `assert 2 == 1`. Overlapped three other runs started 08:51:33–08:52:04. |
| [40077848308](https://github.com/ivanklee86/rubrical/actions/runs/40077848308) | 2026-10-24 08:23:28 | `test_gh_report`: `assert 2 == 1`. Overlapped four other runs started 08:23:07–08:23:38. |
| [40077826932](https://github.com/ivanklee86/rubrical/actions/runs/40077826932) | 2026-10-24 08:23:07 | `test_cli_gh_report` setup error: `404 Not Found` on *delete an issue comment*. |

(The remaining failures in that window were lint, `ty`, and Docker build failures, which are unrelated.)

At the time of writing, PR #27 still has a leftover Rubrical comment (id `6382555631`, created 09:28:36) from the last green run on `main`, which shows that the tests don't clean up even when they pass.

### Root causes

1. **Shared mutable fixture across concurrent runs.** All runs use the same PR and the same fixed comment marker (`[Rubrical](https://github.com/ivanklee86/rubrical) Report`), so run A's comment is indistinguishable from run B's. That leads to three race outcomes:
   - Both runs see no comment and both create one, so the count is 2.
   - Run B's `github_pr_clean` fixture deletes run A's comment between A's lookup and A's `edit()` or `delete()`, so A gets a 404.
   - Run B's fixture tries to delete a comment that run A's fixture already deleted, so B gets a 404 during setup.
2. **Setup-only cleanup, no teardown.** `github_pr_clean` (`tests/fixtures.py`) deletes *every* comment on the PR before the test and nothing after it. `test_gh_report_noop` and `test_cli_gh_report` leave a live comment behind on every run, which the next run has to clean up and might race on.
3. **Cleanup isn't idempotent.** `issue_comment.delete()` raises `UnknownObjectException` when the comment is already gone. Because this runs during fixture setup, the test errors before it starts.
4. **Over-broad cleanup.** The fixture deletes all comments on the PR, including other runs' in-flight comments and any human comments, rather than only what the current test created.
5. **Sleep-based pacing.** `time.sleep(5)` after each delete slows the suite and widens the race window. It doesn't wait for anything specific.
6. **Assertions match too broadly.** `"Rubrical" in issue_comment.body` counts any comment that mentions the word, not just reports from this run.

### Product behavior worth flagging

`report_github()` in `rubrical/reporters/gh.py` keeps the *last* comment that matches the marker and ignores any others. When duplicates exist, whether from these races or from a real user who runs rubrical twice in parallel, rubrical never converges back to one comment, and cleanup only deletes one of them. I don't want tests that enshrine this behavior. Step 3 proposes changing it.

## Goals

- A GitHub test failure means rubrical's GitHub reporting is broken, not that another CI run happened to overlap.
- Each test removes everything it created, even when it fails partway through.
- Most of the reporter's logic is covered without network access, so it runs on forks and locally without a token.
- GitHub calls made by tests can be traced: each comment can be linked back to the run that created it, and created and deleted comment IDs are logged.

## Plan

### 1. Isolate each run's comments with a report ID (product change)

Add an optional report identifier to the GitHub reporter: a `--report-id` option on `grade`, with the environment variable `RUBRICAL_REPORT_ID`. When it is set, the comment body includes a hidden marker `<!-- rubrical:report-id=<id> -->`, and `report_github()` matches only comments that carry that marker. When it is unset, behavior is unchanged: the comment is matched by the existing heading marker, so existing users keep their current comments.

This also has standalone user value. A monorepo that runs rubrical several times on one PR (for example, once per service with different configs) currently has its runs overwrite each other's comment. With report IDs, each run gets its own comment.

Record the decision as an ADR in `docs/adrs/0002-github-report-id.md` and update the Reporting section of `docs/agents/internals.md` and the user docs.

### 2. Rewrite the live-GitHub fixture around ownership and teardown

Replace `github_pr_clean` in `tests/fixtures.py` with a `github_report` fixture that:

- Generates a unique report ID per test invocation: `f"test-{GITHUB_RUN_ID or 'local'}-{GITHUB_RUN_ATTEMPT or 0}-{request.node.name}-{uuid4().hex[:8]}"`.
- Yields `(pr, report_id)`.
- In teardown, which runs even when the test fails, deletes only comments whose body contains that report ID. It treats `UnknownObjectException` (404) as success.
- At setup, sweeps comments with a `rubrical:report-id=test-` marker that are older than a set age (for example, 6 hours). This cleans up after runs that were cancelled or hit a timeout before their teardown ran. The sweep never touches comments without a test marker, and it never touches young comments that may belong to a run still in progress.
- Logs each comment ID it creates, finds or deletes, together with the report ID, through the `logging` module, so `pytest -o log_cli=true` and the CI log show exactly what each run did to PR #27.

Embed the CI run URL (`$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID`) in test-created comments so that someone looking at PR #27 can tell which run left a stray comment. This can go in the report ID itself or in a second hidden marker that only tests set.

Remove `time.sleep(5)`. Where a test needs to observe a write, use a small `wait_for(predicate, timeout=30, interval=1)` helper that polls `pr.get_issue_comments()` until the expected count is reached. This copes with GitHub's eventual consistency without fixed sleeps.

~~Configure PyGithub with a custom `urllib3.Retry` in tests.~~ Dropped during implementation: PyGithub 2.x already defaults to `GithubRetry(total=10)`, which retries 5xx responses and rate limits.

### 3. Make the reporter converge on a single comment

Within one match scope (one report ID, or the legacy marker when there is no ID), change `report_github()` so it:

- Collects *all* matching comments, not just the last one.
- When reporting, edits the first match and deletes the rest.
- When the run is clean, deletes all matches.
- Treats a 404 on `edit()` (another process deleted the comment) by creating a new comment, and a 404 on `delete()` as already done.

This makes the reporter self-heal from duplicates, whatever caused them.

### 4. Move most GitHub coverage off the network

Split `tests/unit/reporters/test_gh.py` into the following:

- **Unit tests (no network).** Fake `Github` / `Repository` / `PullRequest` / `IssueComment` objects (for example, `unittest.mock` with a small in-memory comment list, or the `responses` library pinned to an exact version), injected by monkeypatching `rubrical.reporters.gh.Github`. Planned cases:
  - Happy path: no existing comment and findings present, so one comment is created.
  - Upsert: an existing comment and findings present, so that comment is edited and no new one is created.
  - Cleanup: an existing comment and a clean run, so the comment is deleted.
  - No-op: no comment and a clean run, so there are no write calls and the message says "Nothing to report".
  - Duplicates: two matching comments, so one is edited and the other deleted (step 3).
  - Race on edit: `edit()` raises 404, so a new comment is created.
  - Race on delete: `delete()` raises 404, so no error is raised.
  - Scoping: with report ID `a` set, a comment with report ID `b` and a legacy comment without an ID are both left alone.
  - Legacy compatibility: with no report ID, the existing heading-marker comment is still found and edited.
  - Custom URL: with `custom_url` set, `Github` is constructed with `base_url=<url>/api/v3`.
- **Live integration tests (network, token required).** Keep one live round trip in `tests/integration/test_github.py`: create, then upsert, then clean, with the CLI `test_cli_gh_report` as a second test. Both use the `github_report` fixture and are marked `@pytest.mark.github` (register the marker in `pyproject.toml`). Delete `test_gh_report_noop`. It asserts nothing and leaks a comment.

Tighten assertions to count comments whose body contains this test's report ID, rather than `"Rubrical" in body`.

### 5. CI changes

- Add workflow-level `concurrency: { group: ci-${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true }` to `.github/workflows/ci.yaml`. Renovate force-pushes made `renovate/lock-file-maintenance-python` run CI four times in 12 minutes, and superseded runs should be cancelled. This reduces load. It is not what makes the tests correct; step 1 does that.
- Keep the GitHub tests in the same `pytest` invocation so coverage still includes them, but add `-rs` so skipped GitHub tests show up in the log, for example on fork PRs that have no secret.
- I'm *not* proposing a single global concurrency group to serialize the GitHub tests across runs. GitHub keeps at most one pending job per concurrency group and cancels older pending ones, so a burst of Renovate PRs would get cancelled jobs, which are effectively failures. With per-run report IDs it isn't needed.

### 6. One-off cleanup

After steps 1–4 merge, delete the leftover comment(s) on PR #27 by hand (`gh api -X DELETE repos/ivanklee86/rubrical/issues/comments/<id>`). After that, the age-based sweep in step 2 keeps the PR tidy.

## Order of work

1. Steps 3 and 4 (unit half): reporter convergence and the offline unit tests. These have no product-surface change and can ship on their own. Together with a fixture teardown that ignores 404s, they already remove the 404 failures.
2. Step 1, with its ADR and docs: the report-ID option.
3. Step 2 and the live half of step 4: the new fixture and the rewritten live tests. Together with step 1, these remove the `2 == 1` failures.
4. Step 5: CI concurrency and `-rs`.
5. Step 6: manual cleanup.

## Decisions (formerly open questions)

Answered on 2026-10-24:

- **User-facing `--report-id`: yes.** Implemented as `--report-id` / `RUBRICAL_REPORT_ID`.
- **Duplicate convergence in the legacy (no report ID) path: no.** It applies only when a report ID is set. The legacy path keeps using the last match and leaves the others alone. The 404 tolerance on edit and delete applies to both paths, since it only replaces a crash.
- **Fresh PR per run: no.** Tests keep using PR #27, isolated by report ID.

The original questions:


- Is a user-facing `--report-id` acceptable? The alternative that avoids a product change is a test-only override of the marker string through monkeypatching. It works, but then the live tests no longer exercise the real matching path, and the monorepo use case goes unaddressed.
- Should the duplicate convergence in step 3 also apply to the legacy (no report ID) path? I think yes, but it changes current behavior for users who already have duplicate comments: rubrical would start deleting the extras.
- Should we create a fresh PR per CI run instead of reusing PR #27? It gives the strongest isolation, but it needs `contents: write` to push a branch, and it adds API calls and leaves branches to clean up. I don't recommend it unless report IDs prove insufficient.
