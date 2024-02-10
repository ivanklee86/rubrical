## Package

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
