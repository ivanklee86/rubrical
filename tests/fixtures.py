import os
import time

import pytest
from dotenv import load_dotenv
from github import Github

from tests.constants import GITHUB_REPO_NAME, GITHUB_TEST_PR


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


@pytest.fixture
def github_pr_clean(github_token):
    g = Github(github_token)
    repo = g.get_repo(GITHUB_REPO_NAME)
    pr = repo.get_pull(GITHUB_TEST_PR)

    for issue_comment in pr.get_issue_comments():
        issue_comment.delete()
        time.sleep(5)

    yield pr
