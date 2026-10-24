import logging
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Callable

import pytest
from dotenv import load_dotenv
from github import Auth, Github, UnknownObjectException
from github.PullRequest import PullRequest

from rubrical.reporters import gh
from tests.constants import GITHUB_REPO_NAME, GITHUB_TEST_PR

logger = logging.getLogger(__name__)

TEST_REPORT_ID_PREFIX = "test-"
# Older than any CI run; anything this old with a test marker was orphaned by a cancelled run.
STALE_TEST_COMMENT_AGE = timedelta(hours=6)


@pytest.fixture
def secrets():
    load_dotenv()
    yield


@pytest.fixture
def github_token():
    """Provide GitHub token, skipping test if not available."""
    load_dotenv()
    token = os.getenv("RUBRICAL_TEST_GITHUB_ACCESS_TOKEN")
    if not token:
        pytest.skip("RUBRICAL_TEST_GITHUB_ACCESS_TOKEN not set - skipping GitHub test")
    return token


def wait_for(
    predicate: Callable[[], bool], timeout: float = 30, interval: float = 1
) -> bool:
    """Poll until predicate() is true, to ride out GitHub's eventual consistency."""
    deadline = time.monotonic() + timeout
    while True:
        if predicate():
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(interval)


def owned_comments(pr: PullRequest, report_id: str) -> list:
    marker = gh.report_id_marker(report_id)
    return [c for c in pr.get_issue_comments() if marker in c.body]


def _delete_quietly(comment, reason: str):
    try:
        comment.delete()
        logger.info("Deleted %s comment %s.", reason, comment.id)
    except UnknownObjectException:
        logger.info(
            "%s comment %s was already deleted.", reason.capitalize(), comment.id
        )


def _sweep_stale_test_comments(pr: PullRequest):
    cutoff = datetime.now(timezone.utc) - STALE_TEST_COMMENT_AGE
    stale_marker = f"{gh.REPORT_ID_PREFIX}{TEST_REPORT_ID_PREFIX}"
    for comment in pr.get_issue_comments():
        if stale_marker in comment.body and comment.created_at < cutoff:
            _delete_quietly(comment, "stale")


def _test_report_id(request: pytest.FixtureRequest) -> str:
    # The run ID ties a stray comment on the test PR back to
    # https://github.com/ivanklee86/rubrical/actions/runs/<run id>.
    run_id = os.getenv("GITHUB_RUN_ID", "local")
    run_attempt = os.getenv("GITHUB_RUN_ATTEMPT", "0")
    return f"{TEST_REPORT_ID_PREFIX}{run_id}-{run_attempt}-{request.node.name}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def github_report(github_token, request):
    """Yield (pr, report_id) for a report ID owned by this test, and delete its comments afterwards."""
    g = Github(auth=Auth.Token(github_token))
    pr = g.get_repo(GITHUB_REPO_NAME).get_pull(GITHUB_TEST_PR)
    report_id = _test_report_id(request)
    logger.info(
        "Using report_id=%s on %s#%s.", report_id, GITHUB_REPO_NAME, GITHUB_TEST_PR
    )

    _sweep_stale_test_comments(pr)

    yield pr, report_id

    for comment in owned_comments(pr, report_id):
        _delete_quietly(comment, "owned")
