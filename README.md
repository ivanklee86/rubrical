# rubrical
A Python CLI to encourage (😅) people to update their dependencies!

Supported package managers:
* Jsonnet
* _More coming soon!_


## Installation

### Package

_Coming soon!_

### Docker

_Coming soon!_

## Usage

```bash
rubrical [OPTIONS]
```

| Option | Default Value | Description |
|--------|---------------|-------------|
| --config | rubrical.yaml | Path to configuration file |
| --target | Current folder | Path to source code folder |
| --no-block | n/a | Don't error if blocks found |
| --repository-name | _Unset_ | Repository name for reporting |
| --pr-id | _Unset_ | PR ID for reporting |
| --gh-access-token | _Unset_ | Github access token. Enables Github comments. |
| --gh-custom-url   | _Unset_ | Github Enterprise custom url e.g. https://github.custom.dev |

## Configuration

The `rubrical.yaml` file is used to configure checks for your application.

```yaml
version: 1
package_managers:
  - name: jsonnet
    packages:
      - name: "xunleii/vector_jsonnet" # Name of the dependency
        block: v0.1.0  # If dependency is older than this, error.
        warn: v0.1.2  # If dependency is older than this, warn.
```

## Reporting

### Terminal

Comes for free!

### Github

1. Create a Github access token with `Pull requests: Read and write` permissions.
2. Run rubrical with the `--gh-access-token`, `--repository-name`, and `--pr-id` flags.
