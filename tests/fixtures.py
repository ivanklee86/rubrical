import pytest
from dotenv import load_dotenv


@pytest.fixture
def secrets():
    load_dotenv
    yield


# @pytest.fixture
# def github_comment_clean():
#     g = Github(access_token)
#     repo = g.get_repo(repository_name)
#     pr = repo.get_pull(pr_id)

#     yield
