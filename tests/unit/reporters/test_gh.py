import os

from rubrical.enum import PackageCheck
from rubrical.reporters import gh
from rubrical.schemas.results import PackageCheckResult
from tests.constants import GITHUB_REPO_NAME, GITHUB_TEST_PR
from tests.fixtures import github_pr_clean, secrets  # noqa: F401

DUMMY_RESULTS = {
    "jsonnet": [
        PackageCheckResult(
            name="one",
            file="file1.txt",
            check=PackageCheck.BLOCK,
            version_package="1.1.1",
            version_block="1.1.2",
            version_warn="1.1.3",
        ),
        PackageCheckResult(
            name="one",
            file="file1.txt",
            check=PackageCheck.WARN,
            version_package="1.1.3",
            version_block="1.1.2",
            version_warn="1.1.3",
        ),
        PackageCheckResult(
            name="one",
            file="file1.txt",
            check=PackageCheck.OK,
            version_package="1.1.3",
            version_block="1.1.2",
            version_warn="1.1.3",
        ),
    ],
    "somethingelse": [
        PackageCheckResult(
            name="one",
            file="file1.txt",
            check=PackageCheck.OK,
            version_package="1.1.3",
            version_block="1.1.2",
            version_warn="1.1.3",
        )
    ],
}


def test_gh_report_contents():
    text = gh._generate_report(DUMMY_RESULTS)
    assert "1.1.3 <= 1.1.3" in text
    assert "1.1.1 <= 1.1.2, update to > 1.1.3" in text


def test_gh_report_noop():
    gh.report_github(
        access_token=os.getenv("RUBRICAL_TEST_GITHUB_ACCESS_TOKEN"),
        custom_url="",
        repository_name=GITHUB_REPO_NAME,
        pr_id=GITHUB_TEST_PR,
        reporting_data=DUMMY_RESULTS,
        warnings_found=True,
        blocks_found=True,
    )


def test_gh_report(secrets, github_pr_clean):  # noqa: F811
    pr = github_pr_clean

    # Test creation.
    gh.report_github(
        access_token=os.getenv("RUBRICAL_TEST_GITHUB_ACCESS_TOKEN"),
        custom_url="",
        repository_name=GITHUB_REPO_NAME,
        pr_id=GITHUB_TEST_PR,
        reporting_data=DUMMY_RESULTS,
        warnings_found=True,
        blocks_found=True,
    )

    # Check comment's created.
    comment_count = 0
    for issue_comment in pr.get_issue_comments():
        if "Rubrical" in issue_comment.body:
            comment_count += 1

    assert comment_count == 1

    # Test upsert
    gh.report_github(
        access_token=os.getenv("RUBRICAL_TEST_GITHUB_ACCESS_TOKEN"),
        custom_url="",
        repository_name=GITHUB_REPO_NAME,
        pr_id=GITHUB_TEST_PR,
        reporting_data=DUMMY_RESULTS,
        warnings_found=True,
        blocks_found=True,
    )

    # Check there's still only one comment.
    comment_count = 0
    for issue_comment in pr.get_issue_comments():
        if "Rubrical" in issue_comment.body:
            comment_count += 1

    assert comment_count == 1
