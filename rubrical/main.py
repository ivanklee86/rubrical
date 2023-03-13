from pathlib import Path

import typer
from benedict import benedict

from rubrical.configuration import RubricalConfig
from rubrical.rubrical import Rubrical
from rubrical.utilities import console

app = typer.Typer()


@app.command()
def rubrical(
    config: Path = typer.Option(Path("rubrical.yaml"), help="Path to configuration"),
    target: Path = typer.Option(Path().absolute(), help="Path to configuration"),
    block: bool = typer.Option(True, "/--no-block", help="Don't fail if blocks found."),
):
    console.print_header("Rubrical starting!", "⚙️ ")

    console.print_message("Loading configuration.", "📃")
    if config.suffix in [".yaml", ".json", ".toml"]:
        configuration = RubricalConfig(**benedict(config, format=(config.suffix[1:])))
    else:
        raise ValueError(
            "Rubrical only supports YAML, JSON, or TOML configuration files"
        )

    rubrical = Rubrical(configuration, target)
    (warnings_found, blocks_found) = rubrical.check_package_managers()

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
