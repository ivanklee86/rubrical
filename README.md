# rubrical
A Python CLI to encourage (😅) people to update their dependencies!

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
| --config | rubrical.yaml | Path to configuration file. |
| --target | Current folder | Path to source code folder. |
| --no-block | n/a | Don't error if blocks found. |
| --repository-name | _Unset_ | Repository name for reporting. |
| --pr-id | _Unset_ | PR ID for reporting. |
| --gh-access-token | _Uneset_ | Github access token.  Enables Github comments |

## Reporting

### Terminal

Comes for free!

### Github

1. Create a Github access token with `Pull requests: Read and write` permissions.
2. Run rubrical with the `--gh-access-token`, `--repository-name`, and `--pr-id` flags.
