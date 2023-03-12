from pathlib import Path

import typer
from benedict import benedict

from rubrical.configuration import RubricalConfig
from rubrical.rubrical import Rubrical

app = typer.Typer()


@app.command()
def rubrical(
    config: Path = typer.Option(Path("rubrical.yaml"), help="Path to configuration"),
    target: Path = typer.Option(Path().absolute(), help="Path to configuration"),
):
    if config.suffix in [".yaml", ".json", ".toml"]:
        configuration = RubricalConfig(**benedict(config, format=(config.suffix[1:])))
    else:
        raise ValueError(
            "Rubrical only supports YAML, JSON, or TOML configuration files"
        )

    rubrical = Rubrical(configuration, target)
    rubrical.check_package_managers()


if __name__ == "__main__":
    app()
