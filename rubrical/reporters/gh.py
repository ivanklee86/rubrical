from typing import Dict, List

from github import Github

from rubrical.enum import PackageCheck
from rubrical.schemas.results import PackageCheckResult
from rubrical.utilities import console


def _generate_report(reporting_data: Dict[str, List[PackageCheckResult]]):
    test = """
## [Rubrical](https://github.com/ivanklee86/rubrical) Report

"""

    for package_manager in reporting_data.keys():
        test += f"### {package_manager}\n\n"

        not_ok_results = [
            x
            for x in reporting_data[package_manager]
            if x.check in [PackageCheck.BLOCK, PackageCheck.WARN]
        ]
        if not_ok_results:
            test += "| File | Dependency | Result |\n"
            test += "|------|------------|--------|\n"

            for result in not_ok_results:
                if result.check == PackageCheck.BLOCK:
                    test += f"| {result.file} | {result.name} | ❌ {result.version_package} < {result.version_block}, update to >= {result.version_warn} |\n"
                elif result.check == PackageCheck.WARN:
                    test += f"| {result.file} | {result.name} | ⚠️ {result.version_package} < {result.version_warn}, update to >= {result.version_warn} |\n"
        else:
            test += "🟢 All dependencies up to date!"

    return test


def report_github(
    access_token: str,
    custom_url: str,
    repository_name: str,
    pr_id: int,
    reporting_data: Dict[str, List[PackageCheckResult]],
    warnings_found: bool,
    blocks_found: bool,
):
    # Set up Github
    if custom_url:
        g = Github(base_url=f"{custom_url}/api/v3", login_or_token=access_token)
    else:
        g = Github(access_token)
    repo = g.get_repo(repository_name)
    pr = repo.get_pull(pr_id)

    # Find comment if it exists.
    rubrical_comment = None
    for issue_comment in pr.get_issue_comments():
        if (
            "[Rubrical](https://github.com/ivanklee86/rubrical) Report"
            in issue_comment.body
        ):
            rubrical_comment = issue_comment

    if warnings_found or blocks_found:
        console.print_message("Posting results to Github comment.")
        if rubrical_comment:
            rubrical_comment.edit(_generate_report(reporting_data))
        else:
            pr.create_issue_comment(_generate_report(reporting_data))
    elif rubrical_comment:
        console.print_message("Cleaning up old report.")
        rubrical_comment.delete()
    else:
        console.print_message("Nothing to report, skipping Github.")
