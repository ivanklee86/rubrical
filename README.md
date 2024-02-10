# rubrical

[![CI](https://github.com/ivanklee86/rubrical/actions/workflows/ci.yaml/badge.svg)](https://github.com/ivanklee86/rubrical/actions/workflows/ci.yaml) [![codecov](https://codecov.io/gh/ivanklee86/rubrical/branch/main/graph/badge.svg?token=9WJM4LBDEX)](https://codecov.io/gh/ivanklee86/rubrical) [![PyPI version](https://badge.fury.io/py/rubrical.svg)](https://badge.fury.io/py/rubrical)

A CLI to encourage (😅) people to update their dependencies!

Supported package managers:
* Python (requirements.txt, pyproject.toml (vanilla & poetry))
* Go (go.mod)
* Node.js (package.lock)
* Jsonnet
* _More coming soon!_

![rubrical](https://github.com/ivanklee86/rubrical/blob/main/docs/images/rubrical.png?raw=true)

## Configuration

The `rubrical.yaml` file is used to configure checks for your application.

```yaml
version: 1
package_managers:
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
