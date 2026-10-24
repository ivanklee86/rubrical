import logging
import re
from typing import Dict, List, Optional

from github import Github, UnknownObjectException
from github.IssueComment import IssueComment

from rubrical.enum import PackageCheck
from rubrical.schemas.results import PackageCheckResult
from rubrical.utilities import console

logger = logging.getLogger(__name__)

REPORT_HEADING_MARKER = "[Rubrical](https://github.com/ivanklee86/rubrical) Report"
REPORT_ID_PREFIX = "<!-- rubrical:report-id="
REPORT_ID_PATTERN = re.compile(r"^[A-Za-z0-9._/-]{1,100}$")


def validate_report_id(report_id: str) -> str:
    if report_id and not REPORT_ID_PATTERN.match(report_id):
        raise ValueError(
            "Report ID must be 1-100 characters of letters, digits, '.', '_', '/' or '-'."
        )
    return report_id


def report_id_marker(report_id: str) -> str:
    return f"{REPORT_ID_PREFIX}{report_id} -->"


def _generate_report(
    reporting_data: Dict[str, List[PackageCheckResult]], report_id: str = ""
):
    rep = ""
    if report_id:
        rep += f"{report_id_marker(report_id)}\n"
        rep += f"## {REPORT_HEADING_MARKER}: `{report_id}`\n\n"
    else:
        rep += f"\n## {REPORT_HEADING_MARKER}\n\n"

    for package_manager in reporting_data.keys():  # noqa: PLC0206
        rep += f"### {package_manager}\n\n"

        not_ok_results = [
            x
            for x in reporting_data[package_manager]
            if x.check in [PackageCheck.BLOCK, PackageCheck.WARN]
        ]
        if not_ok_results:
            rep += "| File | Dependency | Result |\n"
            rep += "|------|------------|--------|\n"

            for result in not_ok_results:
                if result.check == PackageCheck.BLOCK:
                    rep += f"| {result.file} | {result.name} | ❌ {result.version_package} < {result.version_block}, update to >= {result.version_warn} |\n"
                elif result.check == PackageCheck.WARN:
                    rep += f"| {result.file} | {result.name} | ⚠️ {result.version_package} < {result.version_warn}, update to >= {result.version_warn} |\n"
        else:
            rep += "🟢 All dependencies up to date!\n"

        rep += "\n"

    return rep.rstrip()


def _is_report_comment(body: str, report_id: str) -> bool:
    if report_id:
        return report_id_marker(report_id) in body
    # Legacy scope: the heading marker, but never a comment owned by a report ID.
    return REPORT_HEADING_MARKER in body and REPORT_ID_PREFIX not in body


def _delete_comment(comment: IssueComment, report_id: str):
    try:
        comment.delete()
        logger.info("Deleted comment %s (report_id=%r).", comment.id, report_id)
    except UnknownObjectException:
        # Someone else deleted it first, which is the outcome we wanted.
        logger.info("Comment %s already deleted (report_id=%r).", comment.id, report_id)


def report_github(
    access_token: str,
    custom_url: str,
    repository_name: str,
    pr_id: int,
    reporting_data: Dict[str, List[PackageCheckResult]],
    warnings_found: bool,
    blocks_found: bool,
    report_id: str = "",
):
    validate_report_id(report_id)

    # Set up Github
    if custom_url:
        g = Github(base_url=f"{custom_url}/api/v3", login_or_token=access_token)
    else:
        g = Github(access_token)
    repo = g.get_repo(repository_name)
    pr = repo.get_pull(pr_id)

    # Find comments in this report's scope.
    matches = [
        issue_comment
        for issue_comment in pr.get_issue_comments()
        if _is_report_comment(issue_comment.body, report_id)
    ]
    logger.info(
        "Found %d report comment(s) on %s#%s (report_id=%r): %s",
        len(matches),
        repository_name,
        pr_id,
        report_id,
        [c.id for c in matches],
    )

    rubrical_comment: Optional[IssueComment]
    if report_id:
        # Converge on one comment: keep the oldest, delete any duplicates.
        rubrical_comment = matches[0] if matches else None
        for duplicate in matches[1:]:
            _delete_comment(duplicate, report_id)
    else:
        # Legacy scope keeps its original behavior: use the last match, leave the rest.
        rubrical_comment = matches[-1] if matches else None

    if warnings_found or blocks_found:
        console.print_message("Posting results to Github comment.")
        report = _generate_report(reporting_data, report_id)
        if rubrical_comment:
            try:
                rubrical_comment.edit(report)
                logger.info(
                    "Edited comment %s (report_id=%r).", rubrical_comment.id, report_id
                )
                return
            except UnknownObjectException:
                logger.info(
                    "Comment %s vanished before edit, creating a new one (report_id=%r).",
                    rubrical_comment.id,
                    report_id,
                )
        created = pr.create_issue_comment(report)
        logger.info("Created comment %s (report_id=%r).", created.id, report_id)
    elif rubrical_comment:
        console.print_message("Cleaning up old report.")
        _delete_comment(rubrical_comment, report_id)
    else:
        console.print_message("Nothing to report, skipping Github.")
