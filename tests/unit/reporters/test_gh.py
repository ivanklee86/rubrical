from itertools import count
from typing import List, Optional

import pytest
from github import UnknownObjectException

from rubrical.enum import PackageCheck
from rubrical.reporters import gh
from rubrical.schemas.results import PackageCheckResult

DUMMY_RESULTS = {
    "jsonnet": [
        PackageCheckResult(
            name="one",
            file="file1.txt",
            check=PackageCheck.BLOCK,
            version_package="1.1.1",
            version_block="1.1.2",
            version_warn="1.1.4",
        ),
        PackageCheckResult(
            name="one",
            file="file1.txt",
            check=PackageCheck.WARN,
            version_package="1.1.3",
            version_block="1.1.2",
            version_warn="1.1.4",
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

DUMMY_CLEAN_RESULTS = {
    "jsonnet": [
        PackageCheckResult(
            name="one",
            file="file1.txt",
            check=PackageCheck.OK,
            version_package="1.1.1",
            version_block="1.1.2",
            version_warn="1.1.4",
        )
    ]
}

LEGACY_BODY = gh._generate_report(DUMMY_RESULTS)
UNRELATED_BODY = "LGTM, thanks!"


class FakeComment:
    def __init__(self, pr: "FakePullRequest", comment_id: int, body: str):
        self._pr = pr
        self.id = comment_id
        self.body = body
        self.vanished = False

    def _check_exists(self):
        if self.vanished or self not in self._pr.comments:
            raise UnknownObjectException(404, message="Not Found")

    def edit(self, body: str):
        self._check_exists()
        self.body = body
        self._pr.writes.append(("edit", self.id))

    def delete(self):
        self._check_exists()
        self._pr.comments.remove(self)
        self._pr.writes.append(("delete", self.id))


class FakePullRequest:
    def __init__(self):
        self.comments: List[FakeComment] = []
        self.writes: List[tuple] = []
        self._ids = count(1)

    def add(self, body: str) -> FakeComment:
        comment = FakeComment(self, next(self._ids), body)
        self.comments.append(comment)
        return comment

    def get_issue_comments(self):
        return list(self.comments)

    def create_issue_comment(self, body: str) -> FakeComment:
        comment = self.add(body)
        self.writes.append(("create", comment.id))
        return comment

    def bodies(self) -> List[str]:
        return [c.body for c in self.comments]


class FakeGithub:
    instances: List["FakeGithub"] = []
    pr: FakePullRequest

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.repository_name: Optional[str] = None
        self.pr_id: Optional[int] = None
        FakeGithub.instances.append(self)

    def get_repo(self, repository_name: str):
        self.repository_name = repository_name
        return self

    def get_pull(self, pr_id: int):
        self.pr_id = pr_id
        return FakeGithub.pr


@pytest.fixture
def fake_pr(monkeypatch) -> FakePullRequest:
    FakeGithub.pr = FakePullRequest()
    FakeGithub.instances = []
    monkeypatch.setattr(gh, "Github", FakeGithub)
    return FakeGithub.pr


def report(findings: bool = True, report_id: str = "", custom_url: str = ""):
    gh.report_github(
        access_token="token",
        custom_url=custom_url,
        repository_name="owner/repo",
        pr_id=7,
        reporting_data=DUMMY_RESULTS if findings else DUMMY_CLEAN_RESULTS,
        warnings_found=findings,
        blocks_found=findings,
        report_id=report_id,
    )


def test_gh_report_contents():
    text = gh._generate_report(DUMMY_RESULTS)
    assert "1.1.1 < 1.1.2, update to >= 1.1.4" in text
    assert "1.1.3 < 1.1.4, update to >= 1.1.4" in text
    assert gh.REPORT_HEADING_MARKER in text
    assert gh.REPORT_ID_PREFIX not in text


def test_gh_report_contents_with_report_id():
    text = gh._generate_report(DUMMY_RESULTS, "service-a")
    assert text.startswith("<!-- rubrical:report-id=service-a -->")
    assert gh.REPORT_HEADING_MARKER in text
    assert "`service-a`" in text


def test_gh_report_targets_requested_pr(fake_pr):
    report()
    (g,) = FakeGithub.instances
    assert g.args == ("token",)
    assert (g.repository_name, g.pr_id) == ("owner/repo", 7)


def test_gh_report_custom_url(fake_pr):
    report(custom_url="https://github.custom.dev")
    (g,) = FakeGithub.instances
    assert g.kwargs == {
        "base_url": "https://github.custom.dev/api/v3",
        "login_or_token": "token",
    }


@pytest.mark.parametrize("report_id", ["", "svc"])
def test_gh_report_creates_comment(fake_pr, report_id):
    fake_pr.add(UNRELATED_BODY)
    report(report_id=report_id)
    assert fake_pr.writes == [("create", 2)]
    assert "update to >= 1.1.4" in fake_pr.comments[1].body


@pytest.mark.parametrize("report_id", ["", "svc"])
def test_gh_report_upserts_existing_comment(fake_pr, report_id):
    report(report_id=report_id)
    report(report_id=report_id)
    assert fake_pr.writes == [("create", 1), ("edit", 1)]
    assert len(fake_pr.comments) == 1


@pytest.mark.parametrize("report_id", ["", "svc"])
def test_gh_report_cleans_up_when_clean(fake_pr, report_id):
    report(report_id=report_id)
    report(findings=False, report_id=report_id)
    assert fake_pr.writes == [("create", 1), ("delete", 1)]
    assert fake_pr.comments == []


def test_gh_report_noop_when_clean_and_no_comment(fake_pr, capsys):
    fake_pr.add(UNRELATED_BODY)
    report(findings=False)
    assert fake_pr.writes == []
    assert "Nothing to report" in capsys.readouterr().out


def test_gh_report_converges_duplicates_with_report_id(fake_pr):
    marker = gh.report_id_marker("svc")
    fake_pr.add(f"{marker}\nold one")
    fake_pr.add(f"{marker}\nold two")
    report(report_id="svc")
    assert fake_pr.writes == [("delete", 2), ("edit", 1)]
    assert len(fake_pr.comments) == 1


def test_gh_report_deletes_all_duplicates_with_report_id_when_clean(fake_pr):
    marker = gh.report_id_marker("svc")
    fake_pr.add(f"{marker}\nold one")
    fake_pr.add(f"{marker}\nold two")
    report(findings=False, report_id="svc")
    assert fake_pr.comments == []


def test_gh_report_legacy_duplicates_keep_original_behavior(fake_pr):
    # Decided in docs/adrs/0002-github-report-id.md: no convergence without a report ID.
    fake_pr.add(LEGACY_BODY)
    fake_pr.add(LEGACY_BODY)
    report()
    assert fake_pr.writes == [("edit", 2)]


def test_gh_report_id_scope_ignores_other_reports(fake_pr):
    fake_pr.add(LEGACY_BODY)
    fake_pr.add(gh._generate_report(DUMMY_RESULTS, "other"))
    report(report_id="svc")
    report(findings=False, report_id="other-svc")
    assert fake_pr.writes == [("create", 3)]


def test_gh_report_id_does_not_match_prefix(fake_pr):
    fake_pr.add(gh._generate_report(DUMMY_RESULTS, "svc-2"))
    report(findings=False, report_id="svc")
    assert fake_pr.writes == []


def test_gh_report_id_ignores_comment_quoting_marker(fake_pr):
    fake_pr.add(f"Why does rubrical post {gh.report_id_marker('svc')}?")
    report(findings=False, report_id="svc")
    report(report_id="svc")
    assert fake_pr.writes == [("create", 2)]
    assert len(fake_pr.comments) == 2


def test_gh_report_legacy_scope_ignores_report_id_comments(fake_pr):
    fake_pr.add(gh._generate_report(DUMMY_RESULTS, "svc"))
    report(findings=False)
    assert fake_pr.writes == []


def test_gh_report_legacy_comment_still_found(fake_pr):
    # A comment from a release that predates report IDs.
    legacy = "\n## [Rubrical](https://github.com/ivanklee86/rubrical) Report\n\n### go"
    fake_pr.add(legacy)
    report()
    assert fake_pr.writes == [("edit", 1)]


@pytest.mark.parametrize("report_id", ["", "svc"])
def test_gh_report_recreates_comment_deleted_before_edit(fake_pr, report_id):
    report(report_id=report_id)
    fake_pr.comments[0].vanished = True
    report(report_id=report_id)
    assert fake_pr.writes == [("create", 1), ("create", 2)]


@pytest.mark.parametrize("report_id", ["", "svc"])
def test_gh_report_tolerates_comment_deleted_before_delete(fake_pr, report_id):
    report(report_id=report_id)
    fake_pr.comments[0].vanished = True
    report(findings=False, report_id=report_id)
    assert fake_pr.writes == [("create", 1)]


@pytest.mark.parametrize(
    "report_id", ["has space", "x-->", "a" * 101, "new\nline", "svc\n", "<b>"]
)
def test_gh_report_rejects_invalid_report_id(fake_pr, report_id):
    with pytest.raises(ValueError):
        report(report_id=report_id)
    assert FakeGithub.instances == []


@pytest.mark.parametrize("report_id", ["svc", "services/api", "test-1.2_3"])
def test_gh_report_accepts_valid_report_id(report_id):
    assert gh.validate_report_id(report_id) == report_id
