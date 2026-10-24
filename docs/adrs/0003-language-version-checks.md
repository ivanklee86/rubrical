---
status: accepted
date: 2026-10-24
---

# 0003: Check declared language versions as a separate construct

## Context and Problem Statement

Rubrical grades dependency versions but not the language versions that a repository declares, such as `requires-python = ">=3.7"`, `go 1.19`, or `"engines": {"node": ">=18.0.0"}`. Teams want to flag repositories that still allow end-of-life runtimes in the same way they flag outdated dependencies.

Two things make this different from dependency checks:

- **Languages and package managers don't map one-to-one.** A Python version can be declared in `pyproject.toml` (PEP 621 or Poetry), `uv.lock`, `.python-version`, `.tool-versions`, `runtime.txt`, or a Dockerfile `FROM` line. Node.js has `engines.node`, `.nvmrc`, and `.node-version`. Several of these files aren't dependency manifests, and some (`.tool-versions`, Dockerfiles) declare several languages at once. A repository can also declare a language without using its package manager.
- **Language declarations are minimums.** They are almost always lower bounds (`>=3.7`, `^3.12`, `go 1.19`). The existing semver comparison grades the highest version a constraint allows: it returns `NOOP` for `GT`/`GTE`, turns `^3.12` into `3.999999.999999` (so it never warns), and treats a two-part version such as `1.19` as unparseable, which gives `OK`. As a result, none of the declarations in our fixtures can be graded today.

How should rubrical model language version checks?

## Considered Options

- **A separate `languages` construct**, with its own config section, its own discovery classes, and a lower-bound comparison.
- **Language checks inside each package manager**, for example a `language` field on `PackageManager` config, read by the existing package manager classes.
- **The language as a synthetic package**, for example `packages: [{name: python, ...}]` under the `python` package manager.

## Decision Outcome

Chosen option: **a separate `languages` construct**, because it is the only option that can read version sources outside dependency manifests, it keeps lower-bound semantics out of the dependency comparison path, and it doesn't collide with real package names (npm has a package called `node`).

- **Configuration.** A new top-level `languages` list, with one `warn`/`block` pair per language. There is no `type` or `packages` list. Language versions are always graded as semver.

  ```yaml
  version: 1
  languages:
    - name: python
      warn: v3.12.0
      block: v3.10.0
  package_managers: []
  ```

- **Discovery.** A `rubrical/languages/` package with a `BaseLanguage` ABC and one subclass per language (`python`, `go`, `nodejs`). Each subclass lists the files it reads and extracts at most one version declaration from each file. File discovery (`rglob` plus the denylist) is extracted from `BasePackageManager` into a shared helper so both constructs use the same discovery code.
- **Comparison.** A new lower-bound comparison grades the *lowest version a declaration allows*.
  - Within a set of AND-ed comparators, the highest lower bound applies. Across `||` alternatives, the lowest applies.
  - Versions are padded to three components, and pre-release suffixes are dropped.
  - The result is `BLOCK` if the lower bound is below `block`, otherwise `WARN` if it is below `warn`, otherwise `OK`. The existing `results_to_status` and `max_status` helpers are reused.
  - If no lower bound can be derived (for example `*` or `<3.12`) or the syntax is invalid, the result is `NOOP`, never `OK`, and the reason is logged with `--debug`.
- **Dialects.** The parser takes a dialect (`GO`, `PEP440`, `POETRY`, or `NPM`), because the official specifications give the same text different meanings. For example, `>3.9` allows `3.9.1` under PEP 440 and Poetry, but `>1.2` means `>=1.3.0` in npm. The rules for each dialect, with sources, are in the plan.
- **Absence.** A file with no declaration for the language produces no result. It doesn't produce `OK`, so every `package.json` in a repository doesn't appear as a passing Node.js check. The exception is `go.mod`: the Go toolchain treats a missing `go` directive as `go 1.16`, so rubrical grades it as `go 1.16 (implicit)`.
- **Unbounded declarations.** npm documents `"node": "*"` as meaning the same as no declaration, so `*` and other declarations with no lower bound give `NOOP` rather than being graded as `0.0.0`.
- **Several declarations.** Each file is graded and reported on its own, the same way dependencies are graded per file. Rubrical doesn't try to reconcile conflicting declarations.
- **Results and reporting.** Language results reuse `PackageCheckResult`, with `name` set to the language. They appear under a `languages` heading in the terminal and in the GitHub comment, and a language `BLOCK` counts toward the exit status like a dependency `BLOCK`.
- **Initial scope.** `go.mod` (`go` directive), `pyproject.toml` (PEP 621 `requires-python` and Poetry `tool.poetry.dependencies.python`), and `package.json` (`engines.node`). Other version files are follow-ups. When a `pyproject.toml` declares both, `requires-python` is graded, because Poetry requires its `python` range to be a subset of `requires-python`.

### Consequences

- Good, because language checks can grow to cover version files (`.python-version`, `.nvmrc`, `.tool-versions`, Dockerfiles) without changing the package manager model.
- Good, because the lower-bound semantics are isolated, so the existing dependency comparisons don't change.
- Good, because a language-only configuration works: `package_managers` becomes optional.
- Neutral, because `go.mod` and `pyproject.toml` are read by both a package manager and a language class. Parsing stays in one place by sharing helpers, but the files are read twice per run.
- Neutral, because `configs jsonschema` output changes. The new field is optional, so existing configurations remain valid.
- Bad, because reporting one result per file can be noisy in monorepos with many `package.json` files. If this is a problem, a later change can add a per-language summary.

## More Information

- Plan: [`docs/agents/plans/language-version-checks.md`](../agents/plans/language-version-checks.md).
- Test fixtures for `engines.node` are in `tests/files/nodejs/engines/`.
