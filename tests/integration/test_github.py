import pytest

from rubrical.enum import PackageCheck
from rubrical.reporters import gh
from rubrical.schemas.results import PackageCheckResult
from tests.constants import GITHUB_REPO_NAME, GITHUB_TEST_PR
from tests.fixtures import (  # noqa: F401
    github_report,
    github_token,
    owned_comments,
    wait_for,
)
from tests.unit.reporters.test_gh import DUMMY_CLEAN_RESULTS, DUMMY_RESULTS

pytestmark = pytest.mark.github

LANGUAGE_RESULTS = {
    "languages": [
        PackageCheckResult(
            name="nodejs",
            file="package.json",
            check=PackageCheck.WARN,
            version_package='engines.node "^18.18.0 || >=21.1.0"',
            version_block="v18.0.0",
            version_warn="v20.0.0",
        ),
        PackageCheckResult(
            name="go",
            file="go.mod",
            check=PackageCheck.BLOCK,
            version_package="go 1.16 (implicit)",
            version_block="v1.20.0",
            version_warn="v1.22.0",
        ),
    ],
    **DUMMY_RESULTS,
}


def report(token: str, report_id: str, findings: bool, reporting_data=None):
    gh.report_github(
        access_token=token,
        custom_url="",
        repository_name=GITHUB_REPO_NAME,
        pr_id=GITHUB_TEST_PR,
        reporting_data=reporting_data
        or (DUMMY_RESULTS if findings else DUMMY_CLEAN_RESULTS),
        warnings_found=findings,
        blocks_found=findings,
        report_id=report_id,
    )


def test_gh_report_round_trip(github_token, github_report):  # noqa: F811
    pr, report_id = github_report

    # Create.
    report(github_token, report_id, findings=True)
    assert wait_for(lambda: len(owned_comments(pr, report_id)) == 1)
    (created,) = owned_comments(pr, report_id)

    # Upsert edits the same comment rather than adding another.
    report(github_token, report_id, findings=True)
    (upserted,) = owned_comments(pr, report_id)
    assert upserted.id == created.id

    # A clean run removes it.
    report(github_token, report_id, findings=False)
    assert wait_for(lambda: owned_comments(pr, report_id) == [])


def test_gh_report_languages_round_trip(github_token, github_report):  # noqa: F811
    pr, report_id = github_report

    report(github_token, report_id, findings=True, reporting_data=LANGUAGE_RESULTS)
    assert wait_for(lambda: len(owned_comments(pr, report_id)) == 1)
    (comment,) = owned_comments(pr, report_id)

    # Languages come first, and `||` survives GitHub's storage escaped.
    assert comment.body.index("### languages") < comment.body.index("### jsonnet")
    assert "| package.json | nodejs |" in comment.body
    assert 'engines.node "^18.18.0 \\|\\| >=21.1.0"' in comment.body
    assert "go 1.16 (implicit) < v1.20.0" in comment.body

    report(github_token, report_id, findings=False)
    assert wait_for(lambda: owned_comments(pr, report_id) == [])
