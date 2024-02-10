
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
* `--debug / --no-debug`: Enable debug messages  [env var: RUBGRICAL_DEBUG; default: no-debug]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
