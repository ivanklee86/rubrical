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
def github_pr_clean():
    g = Github(os.getenv("RUBRICAL_TEST_GITHUB_ACCESS_TOKEN"))
    repo = g.get_repo(GITHUB_REPO_NAME)
    pr = repo.get_pull(GITHUB_TEST_PR)

    for issue_comment in pr.get_issue_comments():
        issue_comment.delete()
        time.sleep(5)

    yield pr
