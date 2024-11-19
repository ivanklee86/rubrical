import base64
import enum
import os
from typing import Optional

from github import Auth, Github, GithubIntegration

from rubrical.enum import GithubAuthType


class CheckStatusConclusionValues(enum):
    ACTION_REQUIRE = "action_required"
    CANCELLED = "canceled"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    SUCCESS = "success"
    SKIPPED = "skipped"
    STALE = "stale"
    TIMED_OUT = "timed_out"


class GithubIntegrationWrapper:
    def __init__(
        self, auth_type=GithubAuthType, custom_url: Optional[str] = ""
    ) -> None:
        self.custom_url: Optional[str] = custom_url
        self.auth_type: GithubAuthType = auth_type

        self.client = None

        if self.auth_type == GithubAuthType.TOKEN:
            self._connect_token()
        elif self.auth_type == GithubAuthType.APP:
            self._connect_type()

    def _connect_token(self):
        access_token = os.getenv("RUBRICAL_GH_TOKEN", "")

        if self.custom_url:
            g = Github(
                base_url=f"{self.custom_url}/api/v3", login_or_token=access_token
            )
        else:
            g = Github(access_token)

        self.client = g

    def _connect_type(self):
        private_key = base64.b64decode(os.getenv("RUBRICAL_GH_PRIVATE_KEY", ""))
        app_id = os.getenv("RUBRICAL_APP_ID", "")

        auth = Auth.AppAuth(app_id=app_id, private_key=private_key)
        if self.custom_url:
            github_integration = GithubIntegration(base_url=self.custom_url, auth=auth)
        else:
            github_integration = GithubIntegration(auth=auth)

        installation = github_integration.get_installations()[0]
        self.client = installation.get_github_for_installations()

    def create_pr_check_status(
        self,
        repo_name: str,
        sha: str,
        conclusion: CheckStatusConclusionValues,
        title: str,
        summary: str,
        text: str,
    ):
        repo = self.client.get_repo(repo_name)
        repo.create_check_run(
            name="Rubrical",
            head_sha=sha,
            status="completed",  # check statuses
            conclusion=conclusion.value,
            output={"title": title, "summary": summary, "text": text},
        )
