# rubrical
A Python CLI to encourage (😅) people to update their dependencies!

Supported package managers:
* Jsonnet
* _More coming soon!_


## Installation

### Package

```
pip install rubrical
```

### Docker

```

```

## Usage

```console
$ rubrical [OPTIONS]
```

**Options**:

* `--config PATH`: Path to configuration  [default: rubrical.yaml]
* `--target PATH`: Path to configuration  [default: /workspaces/rubrical]
* `/--no-block`: Don't fail if blocks found.  [default: True]
* `--repository-name TEXT`: Repository name for reporting purposes.  [env var: RUBRICAL_REPOSITORY]
* `--pr-id INTEGER`: PR ID for reporting purposes.  [env var: RUBRICAL_PR_ID; default: 0]
* `--gh-access-token TEXT`: Github access token for reporting.  Presence will enable Github reporting.  [env var: RUBRICAL_GH_TOKEN]
* `--gh-custom-url TEXT`: Github Enterprise custom url. e.g. https://github.custom.dev  [env var: RUBRICAL_GH_CUSTOM_URL]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

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
