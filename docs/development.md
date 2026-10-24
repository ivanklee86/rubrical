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
* integration:languages:   Run rubrical with languages configuration.
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

## Coverage
1. `task python:test-cov` writes an LCOV report to `test_results/cov.lcov` (plus an HTML report in `test_results/cov_html`).
2. CI reports coverage with [octocov](https://github.com/k1LoW/octocov), configured in `.octocov.yml`. Runs on `main` store a report as a GitHub Actions artifact. Pull requests diff against it and get a coverage comment. The step fails if coverage is below 90%, or (on pull requests) falls more than 0.5 points below `main` or has patch coverage under 85%.
3. [octocov-central](https://github.com/ivanklee86/octocov-central) collects the `main` reports daily and publishes the coverage badge.
4. To check locally, run `task python:test-cov`, then `GITHUB_REPOSITORY=ivanklee86/rubrical octocov` with an [octocov binary](https://github.com/k1LoW/octocov/releases).

## Updating docs
1. Run `task docs:gen` to generate CLI documentation.

## Releasing
1. Create a tag on `main`.
