import pytest

from rubrical.reporters import gh
from tests.constants import GITHUB_REPO_NAME, GITHUB_TEST_PR
from tests.fixtures import (  # noqa: F401
    github_report,
    github_token,
    owned_comments,
    wait_for,
)
from tests.unit.reporters.test_gh import DUMMY_CLEAN_RESULTS, DUMMY_RESULTS

pytestmark = pytest.mark.github


def report(token: str, report_id: str, findings: bool):
    gh.report_github(
        access_token=token,
        custom_url="",
        repository_name=GITHUB_REPO_NAME,
        pr_id=GITHUB_TEST_PR,
        reporting_data=DUMMY_RESULTS if findings else DUMMY_CLEAN_RESULTS,
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
