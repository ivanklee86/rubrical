## Installation

### Package

**Requirements**

* Python 3.12

**Installation**

Rubrical can be installed from [pypi](https://pypi.org/).

```bash
pip install rubrical
```

### Docker

Rubrical is also available as a Docker container.  This is a handy for integrating with a CI/CD system of your choice!

```bash
docker pull ghcr.io/ivanklee86/rubrical:latest
docker run --rm -it --name rubrical \
  -v `pwd`/tests/files:/code ghcr.io/ivanklee86/rubrical:latest \
  --config /code/rubrical.yaml \
  --target /code
```

## Usage

1. Create a [configuration](installation_and_usage.md) file.  This can be commited to your code repositories but to get the most out of rubrical it's highly recommended to maintain a centralized configuration in a repository, gist, etc.
2. In your code repository, run `rubrical grade --config /path/to/config`
3. ???
4. Profit!
