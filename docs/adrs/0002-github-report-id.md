---
status: accepted
date: 2026-10-24
---

# 0002: Scope GitHub report comments with an optional report ID

## Context and Problem Statement

`report_github()` finds its PR comment by the heading marker `[Rubrical](https://github.com/ivanklee86/rubrical) Report`, so every rubrical run on a PR shares one comment. Concurrent CI runs of our own live tests all write to PR #27 and clobber each other's comments, which caused the `assert 2 == 1` and `404 Not Found` flakes described in [`docs/agents/plans/harden-github-integration-tests.md`](../agents/plans/harden-github-integration-tests.md). Users have the same problem in a monorepo that runs rubrical once per service on one PR: each run overwrites or deletes the others' comment. When duplicate comments do appear, the reporter edits the last one and never cleans up the rest.

## Considered Options

- A user-facing `--report-id` option (`RUBRICAL_REPORT_ID`) that scopes the comment with a hidden marker.
- A test-only override of the marker string, applied by monkeypatching.
- A fresh PR for each CI run instead of the shared PR #27.

## Decision Outcome

Chosen option: **a user-facing `--report-id`**. It fixes the test flakes through the real matching path, so the live tests still exercise production code, and it also serves the monorepo use case.

- With a report ID, the comment starts with `<!-- rubrical:report-id=<id> -->` and its heading shows the ID. Only comments that start with exactly that marker match, so a comment that quotes the marker is never edited or deleted. The reporter converges duplicates: it keeps the oldest match and deletes the rest.
- Without a report ID, matching is unchanged: heading marker present, and now also no report-ID marker, so legacy runs leave ID-scoped comments alone. Duplicate convergence is **not** applied to this legacy scope, so existing users with duplicate comments see no behavior change.
- In both scopes, a 404 on edit falls back to creating a comment and a 404 on delete counts as done, instead of crashing the run.
- A report ID is 1–100 characters from `[A-Za-z0-9._/-]`, so it can't break out of the HTML comment.
- Tests keep using the shared PR #27; each test gets a unique report ID and deletes only its own comments.

### Consequences

- Good, because concurrent runs, whether in our CI or a user's monorepo, no longer interfere as long as their report IDs differ.
- Good, because the reporter heals duplicates and concurrent deletes in the report-ID scope.
- Neutral, because changing a run's report ID (or adding one) leaves the comment from the old scope behind; users have to delete it once.
- Bad, because the legacy scope can still accumulate duplicates. Users who hit that can opt into a report ID.
