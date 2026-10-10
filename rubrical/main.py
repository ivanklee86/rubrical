from pathlib import Path
from typing import Optional

import typer

from rubrical.reporters import gh
from rubrical.rubrical import Rubrical
from rubrical.subcommands import configs
from rubrical.utilities import console
from rubrical.utilities.config import load_config

app = typer.Typer()
app.add_typer(configs.app, name="configs")


@app.command()
def grade(
    config: Path = typer.Option(Path("rubrical.yaml"), help="Path to configuration"),
    target: Path = typer.Option(Path().absolute(), help="Path to configuration"),
    block: Optional[bool] = typer.Option(
        None,
        "--block/--no-block",
        help="Fail if blocks found.  Overrides blocking_mode in the configuration.",
        show_default="blocking_mode from configuration",
    ),
    repository_name: str = typer.Option(
        "", envvar="RUBRICAL_REPOSITORY", help="Repository name for reporting purposes."
    ),
    pr_id: int = typer.Option(
        0, envvar="RUBRICAL_PR_ID", help="PR ID for reporting purposes."
    ),
    gh_access_token: str = typer.Option(
        "",
        envvar="RUBRICAL_GH_TOKEN",
        help="Github access token for reporting.  Presence will enable Github reporting.",
    ),
    gh_custom_url: str = typer.Option(
        "",
        envvar="RUBRICAL_GH_CUSTOM_URL",
        help="Github Enterprise custom url. e.g. https://github.custom.dev",
    ),
    debug: bool = typer.Option(
        False,
        # RUBGRICAL_DEBUG is a misspelling kept for backwards compatibility.
        envvar=["RUBRICAL_DEBUG", "RUBGRICAL_DEBUG"],
        help="Enable debug messages",
    ),
):
    """
    A CLI to encourage (😅) people to update their dependencies!
    """

    console.print_header("Rubrical starting!", "⚙️ ")

    configuration = load_config(config)

    rubrical = Rubrical(
        configuration=configuration, repository_path=target, debug=debug
    )
    (warnings_found, blocks_found, check_results) = rubrical.check_package_managers()

    if gh_access_token:
        gh.report_github(
            access_token=gh_access_token,
            custom_url=gh_custom_url,
            repository_name=repository_name,
            pr_id=pr_id,
            reporting_data=check_results,
            warnings_found=warnings_found,
            blocks_found=blocks_found,
        )

    should_block = configuration.blocking_mode if block is None else block

    if blocks_found and should_block:
        console.print_error("Blocked dependencies found!", "🛑")
    elif blocks_found:
        console.print_header(
            "Blocked dependencies found, but blocking is disabled.", "🚧"
        )
    elif warnings_found:
        console.print_header(
            "Warnings, some dependencies may need updating soon!", "☢️ "
        )
    else:
        console.print_header("All dependencies up to date!", "🟢")


if __name__ == "__main__":
    app()
