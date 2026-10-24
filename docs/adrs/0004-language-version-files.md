---
status: accepted
date: 2026-10-24
---

# 0004: Read language version files

## Context and Problem Statement

[ADR 0003](0003-language-version-checks.md) added language version checks for `pyproject.toml`, `go.mod`, and `package.json`, and listed version files as follow-ups. Many repositories pin their runtime only in a version manager's file: `.python-version` (pyenv, uv, setup-python), `.node-version` (nodenv, fnm, setup-node), `.nvmrc` (nvm, fnm, setup-node), or `.go-version` (goenv, setup-go). Those repositories currently get no language result at all.

Version files differ from the manifests that ADR 0003 covers:

- **They pin a version rather than declare a range.** `3.12` in `.python-version` means "use the newest 3.12.x", not "3.12 or newer". The lowest version the pin allows is still the right thing to grade, because it is the runtime the repository will use.
- **Each tool has its own format.** None of them is a range syntax that ADR 0003 already parses. pyenv and goenv read one version per line and use all of them. uv reads a whole line, also accepts PEP 440 specifiers (`>=3.12,<3.13`), and ignores lines that start with `#`. nvm strips `#` comments anywhere in a line, allows exactly one version, and accepts aliases (`lts/*`, `node`). nodenv reads only the first word of `.node-version`.
- **Their contents are often not versions.** `system`, virtualenv names, `pypy3.10`, `cpython@3.12`, `lts/iron`, and `latest` are all valid in at least one tool.

How should rubrical read these files?

## Considered Options

- **New sources in the existing language classes**, with a new dialect for bare version files.
- **Reuse the existing dialects** (npm for Node.js files, PEP 440 for `.python-version`, Go for `.go-version`).
- **A new construct for version-manager files**, separate from languages.

## Decision Outcome

Chosen option: **new sources in the existing language classes, with a new dialect**, because the files declare the same thing that the language checks already grade, so they share the `languages` config, thresholds, and reporting. Reusing existing dialects would accept syntax the tools reject (`>=18 || ^16` in `.nvmrc`) or reject syntax they accept (a bare `3.12` isn't valid PEP 440).

- **Files.** `python` also reads `.python-version`, `nodejs` also reads `.node-version` and `.nvmrc`, and `go` also reads `.go-version`. Each file is graded and reported on its own, the same as in ADR 0003, so a repository with both `pyproject.toml` and `.python-version` gets two Python rows.
- **Out of scope.** `.tool-versions` (asdf and mise), `mise.toml`, `.python-versions`, `runtime.txt`, `uv.lock`, and Dockerfiles. `.tool-versions` declares several languages in one file and can be added later without changing this design.
- **Reading each file.** Each file is read the way the tool that owns it reads it:
  - `.python-version`: every line, trimmed, skipping blank lines and lines that start with `#` (uv).
  - `.go-version`: the first word of every line, skipping blank lines and lines that start with `#` (goenv).
  - `.node-version`: the first word of the file (nodenv).
  - `.nvmrc`: `#` and everything after it is removed, lines are trimmed, blank lines and `key=value` lines are skipped, and exactly one line must remain (nvm).
- **New dialects.**
  - `VERSION_FILE`, used by `.node-version`, `.nvmrc`, and `.go-version`. Each line is a bare version: an optional `v`, then release numbers, then an optional pre-release suffix. Operators, wildcards, and anything else are not gradeable.
  - `PYTHON_VERSION_FILE`, used by `.python-version`. Each line is a bare version, as above, or a PEP 440 specifier set, which uv accepts. Implementation-prefixed requests (`pypy3.10`, `cpython@3.12`, `cpython-3.12.3-macos-aarch64-none`) are not gradeable.
- **Several versions in one file.** pyenv and goenv make every listed version available, so the **lowest** version is graded, which is the same rule as `||` alternatives in ADR 0003.
- **Not gradeable means `NOOP`.** If any line can't be graded (`system`, a virtualenv name, `pypy3.10`, `lts/*`, `latest`), the whole file is `NOOP`, and the reason is logged with `--debug`. One ungradeable line makes the lowest version unknown, so grading the other lines would risk a silent `OK`. This matches the ADR 0003 rule that an unbounded `||` alternative makes the whole declaration ungradeable.
- **Empty files.** A file with no version lines (empty, or only comments) produces no result, the same as a manifest that doesn't declare a version.
- **Reporting.** `raw_constraint` is the file name and each version, quoted, such as `.python-version "3.12" "3.11"`.

### Consequences

- Good, because repositories that pin a runtime only in a version file are now graded.
- Good, because each file follows its own tool's rules, so rubrical doesn't grade content the tool would read differently.
- Neutral, because pins and minimums share thresholds. A pin of `3.12` and a minimum of `>=3.12` both grade as `3.12.0`, which is the intended meaning of a threshold.
- Bad, because a repository that pins `lts/*` or `system` is reported as `NOOP`, and a reviewer has to use `--debug` to see why. This is preferred over guessing which version an alias currently resolves to.
- Bad, because more rows per repository adds to the monorepo noise noted in ADR 0003.

## More Information

- Plan: [`docs/agents/plans/language-version-files.md`](../agents/plans/language-version-files.md).
- Builds on [ADR 0003](0003-language-version-checks.md).
