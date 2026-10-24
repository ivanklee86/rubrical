Rubrical uses a YAML/JSON/TOml file is used to configure checks for your application.  By default, it will use the `rubrical.yaml` in your local directory.  You can specify your own file with the `--config` flag.

```yaml
version: 1
blocking_mode: true  # Optional, default true.  If false, blocked dependencies are reported but rubrical exits 0.
languages:  # Optional.  Grades the language versions your repository declares.
  - name: python  # One of python, go, nodejs.  Each language may only be listed once.
    block: v3.10.0  # If the lowest version allowed is less than this, error.
    warn: v3.12.0  # If the lowest version allowed is less than this, warn.
  - name: go
    block: v1.20.0
    warn: v1.22.0
  - name: nodejs
    block: v18.17.0
    warn: v20.0.0
package_managers:  # Optional.
  - name: jsonnet
    packages:
      - name: "xunleii/vector_jsonnet" # Name of the dependency
        block: v0.1.0  # If dependency is less than this, error.
        warn: v0.1.2  # If dependency is less than this, warn.
  - name: python
    packages:
      - name: Mopidy-Dirble
        block: v1.2.1
        warn: v1.2.2
  - name: go
    packages:
      - name: github.com/adrg/xdg
        block: v0.5.0
        warn: v0.6.0
  - name: nodejs
    packages:
      - name: react
        block: v17.0.3
        warn: v17.0.4
```

The `--block/--no-block` flag on `rubrical grade` overrides `blocking_mode` when given.

### Languages

Language declarations are minimums (e.g. `requires-python = ">=3.10"`), so `rubrical` grades the **lowest version a declaration allows** against `warn` and `block`.  Every file that declares a version is graded and reported separately.

| Language | File | Declaration |
|----------|------|-------------|
| `python` | `pyproject.toml` | `project.requires-python`, or `tool.poetry.dependencies.python` when `requires-python` isn't set. |
| `go` | `go.mod` | The `go` directive.  A `go.mod` without one is graded as `go 1.16`, which is what the Go toolchain assumes. |
| `nodejs` | `package.json` | `engines.node`. |
| `python` | `.python-version` | Every line, as uv reads it.  A line may be a version (`3.12`) or a specifier set (`>=3.12,<3.13`). |
| `go` | `.go-version` | The first word of every line, as goenv reads it. |
| `nodejs` | `.node-version` | The first word of the file, as nodenv reads it. |
| `nodejs` | `.nvmrc` | The single version left after removing `#` comments, as nvm reads it. |

Each file is read with its ecosystem's own range syntax (PEP 440, Poetry, or npm).  For example, `>3.9` allows `3.9.1` in Python, while `>18` means `>=19.0.0` in npm.

* Files that don't declare a version produce no result.
* Declarations with no lower bound, such as `"node": "*"` or `<3.12`, and declarations that aren't valid in their syntax are reported as not gradeable rather than passing.  Run with `--debug` to see why.
* Pre-releases are graded by their release, so `go 1.21rc1` is graded as `1.21.0`.
* A version file that lists several versions (pyenv and goenv make all of them available) is graded by the lowest one.
* Version file entries that aren't versions, such as `system`, a virtualenv name, `pypy3.10`, `cpython@3.12`, `lts/*`, or `latest`, make that file not gradeable.  Rubrical doesn't guess what an alias resolves to.
