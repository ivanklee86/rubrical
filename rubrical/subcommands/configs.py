import json
from pathlib import Path

import typer

from rubrical.schemas.configuration import RubricalConfig
from rubrical.utilities import console
from rubrical.utilities.config import load_config

app = typer.Typer()


@app.command()
def validate(
    config: Path = typer.Option(Path("rubrical.yaml"), help="Path to configuration"),
):
    """
    Validates rubrical config.
    """
    load_config(config)
    console.print_message("Configuration is OK!", "✅")


@app.command()
def jsonschema():
    """
    Prints configuration jsonschema.
    """
    console.print_message(json.dumps(RubricalConfig.model_json_schema(), indent=2))
