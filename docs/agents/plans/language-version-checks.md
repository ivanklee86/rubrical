# Check declared language versions

**Status: implemented** (2026-10-24). See [Implementation notes](#implementation-notes) for where the code differs from this plan. Decisions are recorded in [ADR 0003](../../adrs/0003-language-version-checks.md).

## Problem

Rubrical grades dependency versions but not the language versions that a repository declares. Teams want to warn or block when a repository still allows an end-of-life runtime, such as `requires-python = ">=3.7"` or `go 1.19`.

The existing semver comparison can't grade these declarations, because it grades the *highest* version that a constraint allows, and language declarations are minimums. Here is what each fixture gets today:

| Fixture | Declaration | Today's result | Why |
|---|---|---|---|
| `tests/files/python/pyproject.toml` | `requires-python = ">=3.7"` | `NOOP` | `GTE` always gives `NOOP`. |
| `tests/files/uv/pyproject.toml` | `requires-python = ">=3.14"` | `NOOP` | Same. |
| `tests/files/poetry/pyproject.toml` | `python = "^3.12"` | always `OK` | `COMPATIBLE` becomes `3.999999.999999`. |
| `tests/files/go/go.mod` | `go 1.19` | always `OK` | `semver.compare("1.19", …)` raises `ValueError`, which is treated as `OK`. |
| `tests/files/nodejs/engines/*/package.json` | `engines.node` | not read | The Node.js package manager only reads dependency sections. |

## Goals

- Users can set a `warn` and `block` threshold for each language and get results for every file that declares that language's version.
- A language check is never silently `OK`. If a declaration can't be graded, the result is `NOOP`, and the reason is logged with `--debug`.
- Dependency checks don't change at all.
- Every result can be traced back to the file and the raw declaration it came from.

## Non-goals

- Version files that aren't dependency manifests: `.python-version`, `.nvmrc`, `.node-version`, `.tool-versions`, `runtime.txt`, Dockerfiles, `go.work`. The design supports them, and they are follow-ups.
- The Go `toolchain` directive. Only the `go` directive is graded.
- Reconciling conflicting declarations across files.
- Fixing the existing dependency comparison bugs listed under [Related findings](#related-findings).

## Plan

### 1. Configuration

In `rubrical/enum.py`, add `SupportedLanguages` with `PYTHON = "python"`, `GO = "go"`, and `NODEJS = "nodejs"`. The values match the package manager names, so configs read consistently.

In `rubrical/schemas/configuration.py`:

- Add `LanguageRequirement{name: SupportedLanguages, warn: str, block: str}`.
- Add `languages: List[LanguageRequirement] = []` to `RubricalConfig`.
- Default `package_managers` to `[]`, so a config with only languages is valid.
- Reject duplicate language names with a validator, so it's always clear which thresholds apply.

### 2. Shared file discovery

Extract the `rglob` and denylist loop in `BasePackageManager.read_package_manager_files()` into a function in `rubrical/utilities/files.py`. It should return `Dict[str, FileDetails]`, keyed by the path relative to the target. Rename `PackageManagerFileDetails` to `FileDetails` and keep the old name as an alias, so the package manager code changes as little as possible. `BasePackageManager` then calls the helper. Its behavior doesn't change, and the existing package manager tests cover it.

### 3. Language classes

Create `rubrical/languages/`:

- `base_language.py`: `BaseLanguage` ABC with `name`, `target_files`, `denylist_pathnames`, `found_files`, and `declarations: Dict[str, Package]`. It provides `read_files(target)`, which uses the shared helper, and `parse_files()`, which calls the abstract `parse_file(details) -> Optional[Package]` and stores only the files that return a declaration. Each declaration is a `Package` with `name` set to the language and `raw_constraint` set to the declared value, as written in the file.
- `go.py`: reads `go.mod`, with dialect `GO`. It matches the `^go\s+(\S+)` line. If there's no `go` directive, it records `go 1.16 (implicit)`. It ignores `toolchain`.
- `python.py`: reads `pyproject.toml`. It reads `project.requires-python` with dialect `PEP440`, or failing that `tool.poetry.dependencies.python` with dialect `POETRY`. Denylist: `.venv`, `node_modules`.
- `nodejs.py`: reads `package.json`, specifically `engines.node`, with dialect `NPM`. Denylist: `node_modules`.

Each declaration carries its dialect, either as a field on a small `LanguageDeclaration` dataclass that wraps `Package`, or as a new optional field on `Package`. I'll decide which when implementing; the wrapper is preferred so dependency code doesn't see the new field.

Add `LANGUAGE_MAPPING` next to `PACKAGE_MANAGER_MAPPING` in `rubrical/rubrical.py`.

### 4. Lower-bound comparison

Add `rubrical/comparisons/lower_bound.py` with two functions:

- `lower_bound(raw: str, dialect: Dialect) -> Optional[str]` takes the raw declaration and returns a three-component version, or `None`. `Dialect` is `GO`, `PEP440`, `POETRY`, or `NPM`. A dialect is needed because the same text means different things in different ecosystems (see [Verified syntax rules](#verified-syntax-rules)). Each language class picks the dialect for each source it reads.
- `compare_language(requirement, declaration) -> PackageCheck` returns `NOOP` when `lower_bound` returns `None`. Otherwise it compares the bound with `results_to_status()`.

The algorithm is the same for every dialect. Only the tokenizing and the meaning of each operator differ.

1. Remove whitespace between an operator and its version. All three range syntaxes allow it, for example `>= 3.8` and `> 1.2.3 < 1.2.5`. Then split the range into alternatives and split each alternative into comparators. Alternatives are separated by `||` in npm, and by `||` or `|` in Poetry. PEP 440 has no OR. Comparators are separated by whitespace in npm, commas in PEP 440, and either in Poetry.
2. For each comparator, derive its lower bound using the rules in the table. If a comparator has only an upper bound (`<`, `<=`, `!=`), it contributes nothing.
3. An alternative's lower bound is the **highest** lower bound among its comparators, because comparators are combined with AND. An alternative with no lower bound is unbounded.
4. The declaration's lower bound is the **lowest** lower bound across its alternatives. If any alternative is unbounded, the whole declaration is unbounded, so the function returns `None`.
5. Pad to `MAJOR.MINOR.PATCH` and drop any pre-release, dev, or post suffix, keeping only the release numbers: `1.21rc1` becomes `1.21.0`, `3.13.0rc1` becomes `3.13.0`, and `20.0.0-rc.1` becomes `20.0.0`.
6. If a token is invalid in the dialect, the function returns `None` and logs the reason with `--debug`. Examples: `^` or `||` in PEP 440, `~=3` in PEP 440, a wildcard with an ordered operator in PEP 440 (`>=3.*`), `===` arbitrary equality, or text that isn't a version at all.

I'm writing a small parser rather than adding `packaging` or an npm-range library. No one library handles Go, PEP 440, Poetry, and npm syntax, and only the lower bound is needed. If the parser grows past the rules below, we should revisit that choice.

### Verified syntax rules

These rules were checked against the official documentation on 2026-10-24. Sources are listed at the end of the plan.

| Rule | Go | PEP 440 (`requires-python`) | Poetry (`python`) | npm (`engines.node`) |
|---|---|---|---|---|
| Meaning of the declaration | Minimum toolchain version. Enforced since Go 1.21. | Supported Python versions. | Supported Python versions for locking. It must be a subset of `requires-python`. | Supported Node.js versions. Advisory unless `engine-strict` is set. |
| Operators | None. It's a bare version. | `~=` `==` `!=` `<=` `>=` `<` `>` `===` | PEP 440 operators plus `^` and `~` | `<` `<=` `>` `>=` `=` plus `^`, `~`, hyphen ranges, and X-ranges |
| AND / OR | Not applicable | Comma / none | Comma or whitespace / `\|\|` or `\|` | Whitespace / `\|\|` |
| `>X` lower bound | Not applicable | Next patch: `>3.9` gives `3.9.1`, because PEP 440 says `>1.7` allows `1.7.1` | Next patch: `>3.9` gives `3.9.1`. Poetry builds an exclusive range on the padded version. | Increment the last given component: `>1` gives `2.0.0`, `>1.2` gives `1.3.0`, and `>1.2.3` gives `1.2.4`. node-semver's `replaceXRange` and `minVersion` do this. |
| Bare partial version | `1.19` is the language version, ordered just before `1.19.0`, so it gives `1.19.0` | `==3.12` pads to `3.12.0` | `3.12` is exact and pads to `3.12.0` | `20` is an X-range (`>=20.0.0 <21.0.0-0`), so it gives `20.0.0` |
| Wildcards | Not applicable | Only with `==` and `!=`: `==3.12.*` gives `3.12.0` | `*` means any version, and `3.*` gives `3.0.0` | `*`, `x`, `""` mean any version, and `20.x` gives `20.0.0` |
| Leading `v` / `=` | Not applicable | `v` is ignored | Same as PEP 440 | Both are stripped |
| Missing declaration | Treated as `go 1.16` | No result | No result | No result. npm documents a missing value the same as `*`. |

### What counts as acceptable

These decisions follow from the rules above.

- **Gradeable:** any declaration whose lower bound can be derived with these rules.
- **`NOOP`, logged with `--debug`:** a declaration with no lower bound, such as `*`, `""`, `<3.12`, `!=3.9.*`, or `^18 || <16`. npm documents `*` as meaning the same as no declaration, so grading it as `0.0.0` and blocking would contradict the docs. This is a deliberate difference from node-semver's `minVersion`, which returns `0.0.0` for these ranges.
- **`NOOP`, logged with `--debug`:** syntax that is invalid in the dialect. The tool that owns the file would reject it anyway.
- **Pre-releases:** graded by their release numbers, so `1.21rc1` is graded as `1.21.0`. A release candidate only precedes its own release, so this doesn't hide an end-of-life version.
- **Go with no `go` directive:** graded as `1.16`, with `raw_constraint` set to `go 1.16 (implicit)`. This is what the Go toolchain does, and it's the one case where a missing declaration produces a result.
- **Go `toolchain` directive:** ignored. The docs say it is only a suggestion and can't be lower than the `go` version.
- **Python with both PEP 621 and Poetry:** grade `requires-python`. Poetry requires its `python` range to be a subset of `requires-python`, so `requires-python` is the minimum that users actually see.

### 5. Orchestration and reporting

In `Rubrical`:

- Add `check_languages() -> List[PackageCheckResult]`. For each configured language, it reads and parses files, then appends a `PackageCheckResult(name=language, file=file, check=…, version_package=raw_constraint, version_warn=…, version_block=…)` for each declaration.
- `check_package_managers()` becomes `check_all()`, or gains a languages pass, that also runs `check_languages()`. It calls `terminal.terminal_report("languages", results)`, stores the results under the `languages` key in the results dict, and folds them into `warnings_found` and `blocks_found`.
- Only add the `languages` key when languages are configured, so GitHub comments from existing configs don't change.

`reporters/gh.py` and `reporters/terminal.py` need no changes. They already loop over the result keys, and the "update to >= warn" wording also works for languages. The table column is labeled "Dependency". I'll check whether it reads oddly for languages, and if so rename it to "Name".

### 6. Observability

With `--debug`, log:

- Each file that a language class reads, and whether it found a declaration.
- Each raw declaration, the lower bound derived from it, and the result.
- The reason for each `NOOP` (no lower bound, or unparseable version), so it's always clear why a file wasn't graded.

### 7. Documentation

- `docs/configuration.md`: the `languages` section, with an example.
- `docs/features_and_supported_formats.md`: a table of supported language sources, and the lower-bound and `NOOP` rules.
- `docs/agents/internals.md`: add `rubrical/languages/` and `comparisons/lower_bound.py` to the layout, the languages pass to the flow diagram, and the comparison semantics.
- Mark ADR 0003 as `accepted` once this is merged.

## Tests

### Fixtures

These already exist:

- `tests/files/nodejs/engines/{minimum,caret,range,or-range,wildcard,none}/package.json`
- `tests/files/python/pyproject.toml` (`>=3.7`)
- `tests/files/uv/pyproject.toml` (`>=3.14`)
- `tests/files/poetry/pyproject.toml` (`^3.12`)
- `tests/files/go/go.mod` (`go 1.19`)

Add `tests/files/rubrical-languages.yaml` with thresholds chosen so that every outcome appears at least once:

| Language | warn | block | Expected results |
|---|---|---|---|
| python | `v3.12.0` | `v3.10.0` | `python/` 3.7.0 `BLOCK`, `uv/` 3.14.0 `OK`, `poetry/` 3.12.0 `OK` |
| go | `v1.22.0` | `v1.20.0` | `go/` 1.19.0 `BLOCK` |
| nodejs | `v20.0.0` | `v18.17.0` | `minimum` 18.0.0 `BLOCK`, `range` 18.17.0 `WARN`, `or-range` 18.18.0 `WARN`, `caret` 20.11.0 `OK`, `wildcard` 20.0.0 `OK`, `none` and the existing `package.json` files: no result |

### Test cases

`tests/unit/comparisons/test_lower_bound.py`, for `lower_bound()`. Each case comes from an example in the official docs, or applies a documented rule:

- Go:
  - `1.19` gives `1.19.0`, `1.21.3` gives `1.21.3`, and `1.21rc1` gives `1.21.0`.
  - `>=1.19` gives `None`, because Go has no operators.
- PEP 440:
  - `>=3.7` gives `3.7.0`, `~=3.10` gives `3.10.0`, `==3.12.*` gives `3.12.0`, `==3.12` gives `3.12.0`, and `>=v3.8` gives `3.8.0`.
  - `>3.9` gives `3.9.1`, and `>= 3.8` (with a space) gives `3.8.0`.
  - `>=3.9,<4` gives `3.9.0`, and `>=3.8,>=3.10` gives `3.10.0` because the higher bound wins within AND.
  - Invalid in the dialect, so `None`: `^3.12`, `~=3`, `>=3.*`, `===3.12`, and `>=3.8 || >=3.9`.
  - Unbounded, so `None`: `<3.12`, `!=3.9.*`, and the empty string.
- Poetry:
  - `^3.12` gives `3.12.0`, `~3.12` gives `3.12.0`, `3.*` gives `3.0.0`, and `>3.9` gives `3.9.1`.
  - `>=3.8 <4.0` (whitespace AND) gives `3.8.0`, and `>=3.8,<4.0` (comma AND) gives `3.8.0`.
  - `^3.9 || ^3.11` gives `3.9.0`, and `^3.11 | ^3.9` gives `3.9.0`.
  - `*` gives `None`.
- npm:
  - `>=18.0.0` gives `18.0.0`, `^20.11.0` gives `20.11.0`, `~18.2` gives `18.2.0`, `20.x` gives `20.0.0`, `20` gives `20.0.0`, `=20.1.0` gives `20.1.0`, and `v20.1.0` gives `20.1.0`.
  - `>1` gives `2.0.0`, `>18.2` gives `18.3.0`, and `>18.2.3` gives `18.2.4`. These match node-semver's `minVersion`.
  - `>=18.17.0 <23` gives `18.17.0`, `>= 18.17.0` gives `18.17.0`, `1.2 - 2.3.4` gives `1.2.0`, and `20.0.0-rc.1` gives `20.0.0`.
  - `^18.18.0 || ^20.9.0 || >=21.1.0` gives `18.18.0`, and so does the same range with its alternatives in reverse order.
  - Unbounded, so `None`: `*`, `x`, `""`, `<16`, and `^18 || <16`.
- Any dialect: `banana` gives `None`. It doesn't raise.

For `compare_language()`:

- A bound below `block` gives `BLOCK`.
- A bound between `block` and `warn` gives `WARN`.
- A bound at or above `warn` gives `OK`.
- A bound exactly equal to `block` gives `WARN`, not `BLOCK`.
- An unbounded or unparseable declaration gives `NOOP`, never `OK`.

`tests/unit/languages/test_{go,python,nodejs}.py`, for each language class:

- It extracts the raw declaration and its dialect from each fixture, keyed by relative path.
- It records no entry for files without a declaration (`engines/none`, the root `nodejs/package.json`, and `requirements.txt`, which isn't a target).
- It skips `node_modules`.
- Python:
  - When PEP 621 and Poetry both declare a version, `requires-python` wins.
  - `requires-python` uses the `PEP440` dialect, and Poetry `python` uses the `POETRY` dialect.
- Go:
  - It ignores the `toolchain` directive.
  - A `go.mod` with no `go` directive produces `go 1.16 (implicit)`.

### Fixtures to add

The verified rules above need some fixtures that don't exist yet:

- `tests/files/nodejs/engines/partial-gt/package.json` with `"node": ">18"`. Its lower bound is `19.0.0`, which checks the npm-specific `>` rule end to end.
- `tests/files/nodejs/engines/spaced/package.json` with `"node": ">= 18.17.0"`. This checks whitespace after an operator.
- `tests/files/nodejs/engines/any/package.json` with `"node": "*"`. It should give `NOOP`.
- `tests/files/go-implicit/go.mod` with no `go` directive. It should be graded as `1.16`.
- `tests/files/go-toolchain/go.mod` with `go 1.21rc1` and `toolchain go1.22.0`. It should be graded as `1.21.0`.
- `tests/files/poetry-or/pyproject.toml` with `python = ">=3.8 <3.9 || >=3.10"`. Its lower bound is `3.8.0`.
- `tests/files/python-gt/pyproject.toml` with `requires-python = ">3.9"`. Its lower bound is `3.9.1`.

Update the `rubrical-languages.yaml` expected-results table to include these fixtures, and check that the Go package manager's tests still pass with the new `go.mod` files.

`tests/unit/test_configuration.py`:

- A config with only `languages` is valid.
- An unknown language name is rejected.
- A duplicate language name is rejected.
- Existing configs without `languages` still validate.

`tests/integration/test_cli.py`:

- `grade` with `rubrical-languages.yaml` exits 1, and the output lists each expected `BLOCK` and `WARN` row with its file path.
- With `--no-block`, it exits 0 and still lists the rows.
- The existing CLI tests pass unchanged, which shows that dependency results and exit codes are unaffected.

## Implementation notes

Where the code differs from the plan above:

- **`lower_bound()` raises instead of returning `None`.** It raises `UngradeableError` with a reason ("has no lower bound", "isn't a PEP 440 version specifier", and so on). `compare_language()` catches it and returns a `LanguageGrade{check, lower_bound, reason}`, so the reason can be logged with `--debug`. In the test cases above, "gives `None`" means "raises `UngradeableError`".
- **`LanguageDeclaration` is its own dataclass** (`version`, `raw_constraint`, `dialect`) in `schemas/language.py`, not a wrapper around `Package`. Nothing in the language path needs `Package`'s specification list.
- **`Rubrical.check_all()` was added** and is what `grade` calls. It runs `check_languages()` first, then the unchanged `check_package_managers()`.
- **Report text quotes the declared range**, for example `requires-python ">=3.7" < v3.10.0`. Without the quotes, `engines.node >=18.17.0 <23 < v20.0.0` was hard to read.
- **The GitHub reporter escapes `|` in table cells.** Before this, no reported value could contain `|`, but `||` ranges would have split the markdown table row.
- **Thresholds are parsed with the same version rules.** A `warn` or `block` that isn't a version (for example `latest`) gives `NOOP` with a reason, rather than failing the run.
- **Language test files are named `test_language_*.py`** in `tests/unit/languages/`, because the test directories have no `__init__.py` and `test_go.py`, `test_python.py` and `test_nodejs.py` already exist under `tests/unit/package_managers/`.
- **The "Dependency" column wasn't renamed.** For languages it shows `python`, `go` or `nodejs`, which reads well enough.

## Related findings

These come from reviewing the comparison code. They are out of scope here, but I don't want new tests to enshrine them:

- **Unparseable versions give `OK`.** In `compare_package_semver`, `ValueError` from `semver` produces `OK`, so any dependency pinned to a version that isn't full semver (such as `1.19`) passes silently. It should probably be `NOOP`.
- **`||` ranges are dropped.** `NodeJS._parse_packagelock` skips any dependency whose version contains `||` without logging it, so those dependencies are never graded.
- **Fixed: whitespace after an operator broke npm parsing.** node-semver accepts `>= 1.2.3`, but `NodeJS._parse_packagelock` split on spaces first, so `>= 1.2.3` was graded as a pinned `1.2.3`. The parser now removes whitespace between an operator and its version before parsing.
- **Fixed: bare partial npm versions were graded as exact.** In npm, `20` is an X-range (`>=20.0.0 <21.0.0-0`), but the Node.js package manager mapped it to `EQ` `20`, which semver can't parse, so it got `OK`. Partial versions and every X-range spelling (`1`, `1.2`, `1.x`, `1.x.x`, `1.2.*`) now map to `APPROX_EQ`.
- **Still open: leading `=` and partial versions with `<`.** In npm, `=1.2.3` is the same as `1.2.3`, but rubrical keeps the `=` and fails to parse the version, so it gets `OK`. And `<1.2` means `<1.2.0-0`, but `1.2` can't be parsed as semver, so it also gets `OK`.

## Sources

Checked on 2026-10-24:

- Go: [Go Modules Reference, `go` and `toolchain` directives](https://go.dev/ref/mod#go-mod-file-go), and [Go Toolchains, version syntax and ordering](https://go.dev/doc/toolchain#version).
- Python: [pyproject.toml specification, `requires-python`](https://packaging.python.org/en/latest/specifications/pyproject-toml/), and [Version specifiers (PEP 440)](https://packaging.python.org/en/latest/specifications/version-specifiers/).
- Poetry: [Dependency specification](https://python-poetry.org/docs/dependency-specification/), [pyproject.toml and the `python` requirement](https://python-poetry.org/docs/pyproject/), and [poetry-core constraint parser](https://github.com/python-poetry/poetry-core/blob/main/src/poetry/core/constraints/version/parser.py). The `||`/`|` OR syntax is in the parser but isn't documented on the dependency specification page.
- npm: [package.json `engines`](https://docs.npmjs.com/cli/v10/configuring-npm/package-json#engines), [node-semver README, ranges](https://github.com/npm/node-semver#ranges), [node-semver `range.js`](https://github.com/npm/node-semver/blob/main/classes/range.js), and [node-semver `min-version.js`](https://github.com/npm/node-semver/blob/main/ranges/min-version.js).
