import os

from rubrical.enum import PackageCheck
from rubrical.reporters import gh
from rubrical.results import PackageCheckResult
from tests.constants import GITHUB_REPO_NAME, GITHUB_TEST_PR

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


def test_report_contents():
    text = gh._generate_report(DUMMY_RESULTS)
    assert "1.1.3 <= 1.1.3" in text
    assert "1.1.1 <= 1.1.2, update to > 1.1.3" in text


def test_report():
    gh.report_github(
        os.getenv("RUBRICAL_TEST_GITHUB_TOKEN"),
        GITHUB_REPO_NAME,
        GITHUB_TEST_PR,
        DUMMY_RESULTS,
    )
