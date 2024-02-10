## Development
1. Rubrical includes a `.devcontainer` to instantly* spin up a local or cloud development environment.
2. Develoment tasks are managed through [task](https://taskfile.dev).  Domain-specific tasks are stored in the `task/` folder.
3. Automation for comment tasks can be seen by runing `task --list`

```bash
* docker:build:            Builds Docker container for local testing.
* docker:run:              Runs Rubrical in Docker container.
* docker:shell:            Runs Rubrical in Docker container.
* docs:gen:                Generates CLI docs
* docs:release:            Publish docs to Github Pages.
* docs:serve:              Run mkdocs server locally.
* integration:block:       Run rubrical with block configuration.
* integration:clean:       Run rubrical with clean configuration.
* integration:mixed:       Run rubrical with mixed configuration.  (Used for docs)
* integration:warn:        Run rubrical with warn configuration.
* python:build:            Build artifact
* python:fmt:              Run linting and fix issues.
* python:install:          Install dependencies.
* python:lint:             Run linting tasks.
* python:publish:          Publish package to pypi
* python:test:             Run unit and integration tests
* python:test-cov:         Run unit and integration tests with coverage
```

## Updating docs
1. Run `task docs:gen` to generate CLI documentation.

## Releasing
1. Create a tag on `main`.
