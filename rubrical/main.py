from pathlib import Path

import typer
from benedict import benedict

from rubrical.reporters import gh
from rubrical.rubrical import Rubrical
from rubrical.schemas.configuration import RubricalConfig
from rubrical.utilities import console

app = typer.Typer()


@app.command()
def rubrical(
    config: Path = typer.Option(Path("rubrical.yaml"), help="Path to configuration"),
    target: Path = typer.Option(Path().absolute(), help="Path to configuration"),
    block: bool = typer.Option(True, "/--no-block", help="Don't fail if blocks found."),
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
        False, envvar="RUBGRICAL_DEBUG", help="Enable debug messages"
    ),
):
    """
    A CLI to encourage (😅) people to update their dependencies!
    """

    console.print_header("Rubrical starting!", "⚙️ ")

    console.print_message("Loading configuration.", "📃")
    if config.suffix in [".yaml", ".json", ".toml"]:
        configuration = RubricalConfig(**benedict(config, format=(config.suffix[1:])))
    else:
        raise ValueError(
            "Rubrical only supports YAML, JSON, or TOML configuration files"
        )

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

    if blocks_found and block:
        console.print_error("Blocked dependencies found!", "🛑")
    elif warnings_found:
        console.print_header(
            "Warnings, some dependencies may need updating soon!", "☢️ "
        )
    else:
        console.print_header("All dependencies up to date!", "🟢")


if __name__ == "__main__":
    app()
