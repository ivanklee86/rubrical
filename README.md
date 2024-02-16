# rubrical

[![CI](https://github.com/ivanklee86/rubrical/actions/workflows/ci.yaml/badge.svg)](https://github.com/ivanklee86/rubrical/actions/workflows/ci.yaml) [![codecov](https://codecov.io/gh/ivanklee86/rubrical/branch/main/graph/badge.svg?token=9WJM4LBDEX)](https://codecov.io/gh/ivanklee86/rubrical) [![PyPI version](https://badge.fury.io/py/rubrical.svg)](https://badge.fury.io/py/rubrical)

A CLI to encourage (😅) people to update their dependencies!

## raison d'etre

```gherkin
Scenario: A team publishes an update to a new library that needs to be adopted.
            (New feature, breaking changes, security fixes, etc)
  Given your company has a microservice architecture
          (or >3 repositories to update across >2 teams )
  Then you go to each team and beg/bargin/plead for them to update their packages
```

You can (should!) use tools like [renovate](https://github.com/renovatebot/renovate) to automate dependency updates.  But it's easy to lose track of updates especially with particularly technologies (hi JS/TS!) or busy teams.

`rubrical` breaks the cycle by putting a check inside your CI/CD pipelines. (Golden pipelines or shared workflows are highly recommended!)  Now teams have a tool to automatically (automagically!) communicated when a dependency needs to be upgraded!

For more information, checkout the [documentation](https://ivanklee86.github.io/rubrical/)!

## Features
- Set warning (notify users their dependency will be out of date soon) and block (exit with error code) levels.
- Supports different languages (Python, Go, Node.js, and Jsonnet) and package manager formats (e.g. pip, poetry).
- Post results to Github/GHE PRs.

![rubrical](https://github.com/ivanklee86/rubrical/blob/main/docs/images/rubrical.png?raw=true)
