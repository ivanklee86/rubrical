from pathlib import Path

import click
import pytest
from typer.testing import CliRunner

from rubrical.main import app
from tests.constants import BASE_TEST_PATH, GITHUB_REPO_NAME, GITHUB_TEST_PR
from tests.fixtures import (  # noqa: F401
    github_report,
    github_token,
    owned_comments,
    wait_for,
)

runner = CliRunner()


def test_cli_basic():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
            "--debug",
        ],
        env={"COLUMNS": "250"},
    )
    assert result.exit_code == 1
    assert "update to" in result.stdout
    assert 'requires-python ">=3.7" < v3.8.0' in result.stdout


def test_cli_warning():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical-warnings.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
        ],
        env={"COLUMNS": "250"},
    )
    assert not result.exit_code
    assert "Warnings" in result.stdout
    assert "go 1.16 (implicit) < v1.20.0" in result.stdout
    assert "❌" not in result.stdout


def test_cli_clean():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical-clean.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
        ],
    )
    assert not result.exit_code
    assert "up to date" in result.stdout
    assert "languages checks completed with no warnings or blocks" in result.stdout


@pytest.mark.github
def test_cli_gh_report(github_token, github_report):  # noqa: F811
    pr, report_id = github_report

    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
            "--repository-name",
            GITHUB_REPO_NAME,
            "--pr-id",
            str(GITHUB_TEST_PR),
            "--gh-access-token",
            github_token,
            "--report-id",
            report_id,
        ],
    )
    assert result.exit_code == 1
    assert "update to" in result.stdout

    assert wait_for(lambda: len(owned_comments(pr, report_id)) == 1)
    (comment,) = owned_comments(pr, report_id)
    assert "### languages" in comment.body
    assert 'requires-python ">=3.7" < v3.8.0' in comment.body
    # `||` is escaped so the range stays in its table cell.
    assert 'engines.node "^18.18.0 \\|\\| ^20.9.0 \\|\\| >=21.1.0"' in comment.body


def test_cli_gh_report_passes_report_id_from_env(mocker):
    report_github = mocker.patch("rubrical.main.gh.report_github")
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
        ],
        env={"RUBRICAL_GH_TOKEN": "token", "RUBRICAL_REPORT_ID": "service-a"},
    )
    assert result.exit_code == 1
    assert report_github.call_args.kwargs["report_id"] == "service-a"


def test_cli_gh_report_includes_languages(mocker):
    report_github = mocker.patch("rubrical.main.gh.report_github")
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical-warnings.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
        ],
        env={"RUBRICAL_GH_TOKEN": "token"},
    )
    assert not result.exit_code

    kwargs = report_github.call_args.kwargs
    assert list(kwargs["reporting_data"].keys())[0] == "languages"
    assert {x.name for x in kwargs["reporting_data"]["languages"]} == {
        "python",
        "go",
        "nodejs",
    }
    assert kwargs["warnings_found"]
    assert not kwargs["blocks_found"]


def test_cli_rejects_invalid_report_id():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
            "--report-id",
            "not valid",
        ],
    )
    assert result.exit_code == 2
    assert "--report-id" in click.unstyle(result.output)


def test_cli_configs_jsonschema():
    result = runner.invoke(
        app,
        ["configs", "jsonschema"],
    )
    assert not result.exit_code


def test_cli_configs_validate_successful():
    result = runner.invoke(
        app,
        [
            "configs",
            "validate",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical.yaml")),
        ],
    )
    assert not result.exit_code


def test_cli_configs_validate_failure():
    result = runner.invoke(
        app,
        [
            "configs",
            "validate",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical-error.yaml")),
        ],
    )
    assert result.exit_code


def test_cli_grade_invalid_config():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical-error.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
        ],
    )
    assert result.exit_code == 1
    assert not isinstance(result.exception, NameError)
    assert "Configuration error found!" in result.stdout


def test_cli_debug_envvar():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical-clean.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
        ],
        env={"RUBRICAL_DEBUG": "1"},
    )
    assert not result.exit_code
    assert "Debug:" in result.stdout


def test_cli_no_block_flag():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
            "--no-block",
        ],
    )
    assert not result.exit_code
    assert "blocking is disabled" in result.stdout
    assert "up to date" not in result.stdout


def test_cli_blocking_mode_config():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical-nonblocking.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
        ],
        env={"COLUMNS": "250"},
    )
    assert not result.exit_code
    assert "blocking is disabled" in result.stdout
    assert 'requires-python ">=3.7" < v3.8.0' in result.stdout


@pytest.mark.parametrize(
    "flags,exit_code", [([], 0), (["--block"], 1)], ids=["config", "block-flag"]
)
def test_cli_blocking_mode_languages_only(tmp_path, flags, exit_code):
    # Language blocks alone follow blocking_mode, without any package blocks.
    config = Path(tmp_path, "rubrical.yaml")
    config.write_text(
        "version: 1\n"
        "blocking_mode: false\n"
        "languages:\n"
        "  - name: go\n"
        "    block: v1.20.0\n"
        "    warn: v1.22.0\n"
    )

    result = runner.invoke(
        app,
        ["grade", "--config", str(config), "--target", str(BASE_TEST_PATH), *flags],
    )
    assert result.exit_code == exit_code
    assert "go 1.19" in result.stdout


def test_cli_block_flag_overrides_blocking_mode_config():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical-nonblocking.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
            "--block",
        ],
    )
    assert result.exit_code == 1
    assert "Blocked dependencies found!" in result.stdout


def test_cli_languages():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical-languages.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
        ],
        env={"COLUMNS": "250"},
    )
    assert result.exit_code == 1
    assert "Grading languages" in result.stdout
    assert 'requires-python ">=3.7" < v3.10.0' in result.stdout
    assert "go 1.16 (implicit) < v1.20.0" in result.stdout
    assert 'engines.node "^18.18.0 || ^20.9.0 || >=21.1.0" < v20.0.0' in result.stdout
    # Declarations at or above `warn`, or without a lower bound, aren't reported.
    assert '"^20.11.0"' not in result.stdout
    assert 'engines.node "*"' not in result.stdout


def test_cli_languages_no_block():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical-languages.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
            "--no-block",
        ],
    )
    assert not result.exit_code
    assert "blocking is disabled" in result.stdout
