from pathlib import Path

from benedict import benedict
from pydantic import ValidationError

from rubrical.schemas.configuration import RubricalConfig
from rubrical.utilities import console


def load_config(config: Path) -> RubricalConfig:
    console.print_message("Loading configuration.", "📃")
    if config.suffix not in [".yaml", ".json", ".toml"]:
        raise ValueError(
            "Rubrical only supports YAML, JSON, or TOML configuration files"
        )

    try:
        return RubricalConfig(**benedict(config, format=(config.suffix[1:])))  # ty: ignore
    except ValidationError as e:
        console.print_raw(str(e))
        console.print_error("Configuration error found!", "🔴")
