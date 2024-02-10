import os
from pathlib import Path

from typer.testing import CliRunner

from rubrical.main import app
from tests.constants import BASE_TEST_PATH, GITHUB_REPO_NAME, GITHUB_TEST_PR
from tests.fixtures import github_pr_clean, secrets  # noqa: F401

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
    )
    assert result.exit_code == 1
    assert "update to" in result.stdout


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
    )
    assert not result.exit_code
    assert "Warnings" in result.stdout


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


def test_cli_gh_report(secrets, github_pr_clean):  # noqa: F811
    pr = github_pr_clean

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
            GITHUB_TEST_PR,
            "--gh-access-token",
            os.getenv("RUBRICAL_TEST_GITHUB_ACCESS_TOKEN"),
        ],
    )
    assert result.exit_code == 1
    assert "update to" in result.stdout

    # Check there's still only one comment.
    comment_count = 0
    for issue_comment in pr.get_issue_comments():
        if "Rubrical" in issue_comment.body:
            comment_count += 1

    assert comment_count == 1
