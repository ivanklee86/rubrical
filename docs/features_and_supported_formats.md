## Application

* Users can configure warning (notifications) or block (error out) levels for pcakges.
* `rubrical` will recursively search repository for dependency definition files (e.g. requirements.txt, package.json, etc) for languages with configured checks.
* `rubrical` supports reporting results to command line and Github comments.  See [reporting](reporting.md).

## Languages and Package Managers

| Language | Package Managers |
|----------|------------------|
| Python | `requirements.txt`, `pyproject.toml` (vanilla & Poetry) |
| Go | `go.mod` |
| Node.js | `package.json` |
| jsonnet | `jsonnetfile.json` |

## Language versions

`rubrical` can also check the language version a repository declares.  See [configuration](configuration.md#languages).

| Language | Declarations |
|----------|--------------|
| Python | `pyproject.toml` (`requires-python` & Poetry `python`) |
| Go | `go.mod` (`go` directive) |
| Node.js | `package.json` (`engines.node`) |
