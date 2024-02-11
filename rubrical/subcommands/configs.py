import json
from pathlib import Path

import typer
from benedict import benedict
from pydantic import ValidationError

from rubrical.schemas.configuration import RubricalConfig
from rubrical.utilities import console

app = typer.Typer()


@app.command()
def validate(
    config: Path = typer.Option(Path("rubrical.yaml"), help="Path to configuration"),
):
    """
    Validates rubrical config.
    """
    console.print_message("Loading configuration.", "📃")
    if config.suffix in [".yaml", ".json", ".toml"]:
        try:
            RubricalConfig(**benedict(config, format=(config.suffix[1:])))
        except ValidationError as e:
            console.print_raw(str(e))
            console.print_error("Configuration error found!", "🔴")
    else:
        raise ValueError(
            "Rubrical only supports YAML, JSON, or TOML configuration files"
        )

    console.print_message("Configuration is OK!", "✅")


@app.command()
def jsonschema():
    """
    Prints configuration jsonschema.
    """
    console.print_message(json.dumps(RubricalConfig.model_json_schema(), indent=2))
