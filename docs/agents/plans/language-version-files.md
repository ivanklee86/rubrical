# Read language version files

**Status: implemented** (2026-10-24). Decisions are recorded in [ADR 0004](../../adrs/0004-language-version-files.md), which builds on [ADR 0003](../../adrs/0003-language-version-checks.md) and [its plan](language-version-checks.md).

## Problem

Language checks read only `pyproject.toml`, `go.mod`, and `package.json`. A repository that pins its runtime only in `.python-version`, `.node-version`, `.nvmrc`, or `.go-version` gets no language result, even though CI (setup-python, setup-node, setup-go) and local tooling use that file to pick the runtime.

## Goals

- Grade `.python-version`, `.node-version`, `.nvmrc`, and `.go-version` with the existing `languages` config, thresholds, and reporting.
- Read each file the way the tool that owns it reads it, so rubrical doesn't grade content the tool would interpret differently.
- Keep the ADR 0003 rule that a language check is never silently `OK`: anything that can't be graded is `NOOP` with a reason logged under `--debug`.

## Non-goals

- `.tool-versions`, `mise.toml`, uv's `.python-versions`, `runtime.txt`, `uv.lock`, and Dockerfiles.
- Resolving aliases (`lts/*`, `node`, `latest`, `system`) or implementation-prefixed requests (`pypy3.10`, `cpython@3.12`) to a version.
- Reconciling a version file with the manifest in the same directory.

## Verified file formats

Checked against each tool's source or documentation on 2026-10-24. Sources are listed at the end.

| File | Tool rules | How rubrical reads it |
|---|---|---|
| `.python-version` | **pyenv** reads every line, keeps the first word of each, skips blank lines and lines whose first word starts with `#`, and uses all versions. **uv** reads every line, trimmed, skips blank lines and lines that start with `#`, and parses the whole line as a request: a version (`3.12`), a PEP 440 specifier set (`>=3.12,<3.13`), a variant (`3.13t`, `3.13+freethreaded`), an implementation (`pypy3.10`, `cpython@3.12`, `cpython-3.12.3-macos-aarch64-none`), or a path or executable name. | uv's rules: every trimmed line that is not blank and doesn't start with `#`. A trailing comment (`3.12 # pinned`), which pyenv allows and uv doesn't, isn't gradeable. |
| `.go-version` | **goenv** reads the first word of every line, skips blank lines and lines whose first word starts with `#`, drops `..` and words containing `/`, and uses all versions. setup-go accepts the file through `go-version-file`. | The first word of every line that is not blank and doesn't start with `#`. |
| `.node-version` | **nodenv** reads only the first word of the file, with no comment handling. setup-node accepts the file through `node-version-file`. | The first word of the file. |
| `.nvmrc` | **nvm** removes `#` and everything after it on each line, trims each line, and skips blank lines. A line containing `=` is a reserved `key=value` pair and is ignored. Exactly one other line must remain, or the file is invalid. Aliases such as `lts/*`, `lts/iron`, `node`, and `stable` are allowed. | nvm's rules. If more than one version line remains, the lines are kept together as one value, which isn't gradeable. |

## Plan

### 1. Dialects

Add two values to `VersionDialect` and register them in `DIALECTS` in `comparisons/lower_bound.py`.

| Dialect | Used by | Alternatives | Comparator |
|---|---|---|---|
| `VERSION_FILE` | `.node-version`, `.nvmrc`, `.go-version` | One per line. | A bare version: an optional `v`, release numbers, and an optional pre-release suffix. An operator, wildcard, or anything else raises `UngradeableError`. |
| `PYTHON_VERSION_FILE` | `.python-version` | One per line. A line that starts with an operator is split into PEP 440 comparators. | A bare version, as above, or a PEP 440 comparator. |

Each line is an alternative, so the existing `lower_bound()` loop gives the lowest version across lines, and one ungradeable line makes the whole file `NOOP`. Bare versions are padded and suffixes are dropped as in ADR 0003, so `3.13t` grades as `3.13.0` and `v18.17.1` as `18.17.1`.

### 2. Reading files

Add `rubrical/languages/version_files.py` with one function per file format, each returning the version lines (an empty list means the file declares nothing). The language classes add the file names to `target_files` and dispatch on `file_details.path.name` in `parse_file`. A file whose function returns no lines returns `None`, so it produces no result.

`raw_constraint` is the file name followed by each line quoted, for example `.python-version "3.12" "3.11"`, and `version` is the lines joined by newlines.

### 3. Observability

`Rubrical.check_languages()` already logs each declaration, its lower bound, and the `NOOP` reason under `--debug`, so no new logging is needed. The `UngradeableError` reasons name the offending line, for example ``\`pypy3.10\` is not a version``.

### 4. Documentation

- `docs/configuration.md` and `docs/features_and_supported_formats.md`: add the four files.
- `docs/agents/internals.md`: add the files to the language table, the new dialects, and `version_files.py`.

## Tests

Fixtures in `tests/files/version-files/`, graded with `rubrical-languages.yaml` (Python warn `3.12.0`/block `3.10.0`, Go warn `1.22.0`/block `1.20.0`, Node.js warn `20.0.0`/block `18.17.0`):

| Fixture | Contents | Expected |
|---|---|---|
| `python/.python-version` | `3.12` | `OK` |
| `python-multi/.python-version` | a comment, `3.12.4`, `3.9` | `BLOCK` (lowest is `3.9.0`) |
| `python-specifier/.python-version` | `>=3.11, <3.13` | `WARN` |
| `python-pypy/.python-version` | `pypy3.10` | `NOOP` |
| `python-system/.python-version` | `3.12`, `system` | `NOOP` |
| `go/.go-version` | `1.21.5` | `WARN` |
| `node/.node-version` | `v18.17.1` | `WARN` |
| `nvmrc/.nvmrc` | a comment line, `20 # LTS` | `OK` |
| `nvmrc-lts/.nvmrc` | `lts/*` | `NOOP` |

Unit tests in `tests/unit/comparisons/test_lower_bound.py`:

- `VERSION_FILE`: `20` gives `20.0.0`, `v18.17.1` gives `18.17.1`, `1.21rc1` gives `1.21.0`, and `1.22.0\n1.21.5` gives `1.21.5`.
- `VERSION_FILE` is not gradeable for `lts/*`, `node`, `latest`, `>=18`, `20.x`, `20 18` (two `.nvmrc` versions), and `20\nlts/*`.
- `PYTHON_VERSION_FILE`: `3.12` gives `3.12.0`, `3.13t` and `3.13+freethreaded` give `3.13.0`, `>=3.11, <3.13` gives `3.11.0`, and `3.12\n3.9` gives `3.9.0`.
- `PYTHON_VERSION_FILE` is not gradeable for `pypy3.10`, `cpython@3.12`, `cpython3.12`, `system`, `my-venv`, `3.12 # pinned`, `<3.13`, and `3.12\nsystem`.

Unit tests in `tests/unit/languages/` for each reader, through `parse_file`:

- `.python-version`: comments and blank lines are skipped; every line is kept; a file with only comments returns `None`.
- `.go-version`: the first word of each line is kept; comment lines are skipped.
- `.node-version`: only the first word of the file is kept.
- `.nvmrc`: inline comments and `key=value` lines are removed; two version lines are kept together and aren't gradeable; a file with only `key=value` lines returns `None`.
- Each class finds the fixtures under `tests/files/` with the expected dialect, and the existing manifests are still found.

`tests/unit/test_rubrical.py`: `test_rubrical_languages` expects the rows in the fixture table.

## Sources

Checked on 2026-10-24:

- pyenv: [`pyenv-version-file-read`](https://github.com/pyenv/pyenv/blob/master/libexec/pyenv-version-file-read).
- uv: [Python versions, `.python-version` files and request formats](https://docs.astral.sh/uv/concepts/python-versions/), and [`version_files.rs`](https://github.com/astral-sh/uv/blob/main/crates/uv-python-discovery/src/version_files.rs).
- goenv: [`goenv-version-file-read`](https://github.com/go-nv/goenv/blob/master/libexec/goenv-version-file-read). setup-go: [README, `go-version-file`](https://github.com/actions/setup-go#readme).
- nodenv: [`nodenv-version-file-read`](https://github.com/nodenv/nodenv/blob/master/libexec/nodenv-version-file-read).
- nvm: [README, `.nvmrc`](https://github.com/nvm-sh/nvm#nvmrc), and [`nvm_process_nvmrc_content` in `nvm.sh`](https://github.com/nvm-sh/nvm/blob/master/nvm.sh).
- setup-node: [README, supported version syntax](https://github.com/actions/setup-node#supported-version-syntax), and [advanced usage, `node-version-file`](https://github.com/actions/setup-node/blob/main/docs/advanced-usage.md).
