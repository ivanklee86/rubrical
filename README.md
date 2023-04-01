# rubrical

[![CI](https://github.com/ivanklee86/rubrical/actions/workflows/ci.yaml/badge.svg)](https://github.com/ivanklee86/rubrical/actions/workflows/ci.yaml) [![codecov](https://codecov.io/gh/ivanklee86/rubrical/branch/main/graph/badge.svg?token=9WJM4LBDEX)](https://codecov.io/gh/ivanklee86/rubrical) [![PyPI version](https://badge.fury.io/py/rubrical.svg)](https://badge.fury.io/py/rubrical)

A CLI to encourage (😅) people to update their dependencies!

Supported package managers:
* Python (requirements.txt)
* Jsonnet
* _More coming soon!_

![rubrical](docs/images/rubrical.png)

## Installation

### Package

```
pip install rubrical
```

### Docker

```
docker pull ghcr.io/ivanklee86/rubrical:latest
docker run --rm -it --name rubrical -v `pwd`/tests/files:/code ghcr.io/ivanklee86/rubrical:latest --config /code/rubrical.yaml --target /code
```

## Usage

```console
$ rubrical [OPTIONS]
```

**Options**:

* `--config PATH`: Path to configuration  [default: rubrical.yaml]
* `--target PATH`: Path to configuration  [default: /workspaces/rubrical]
* `/--no-block`: Don't fail if blocks found.  [default: True]
* `--debug / --no-debug`: Enable debug messages  [default: no-debug]
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
  - name: python
    packages:
      - name: Mopidy-Dirble
        block: v1.2.1
        warn: v1.2.2
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
