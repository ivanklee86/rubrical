# ruff: noqa: PLR2004
import pytest
from pydantic import ValidationError

from rubrical.schemas.configuration import RubricalConfig

TEST_CONFIG = {
    "version": 1,
    "package_managers": [
        {
            "name": "jsonnet",
            "packages": [
                {"name": "dep1", "warn": "v1.0.0", "block": "v0.5.0"},
                {
                    "name": "dep1",
                    "type": "generic",
                    "warn": "v1.0.0",
                    "block": "v0.5.0",
                },
            ],
        }
    ],
}


def test_config_load():
    test_config = RubricalConfig(**TEST_CONFIG)  # ty: ignore
    assert len(test_config.package_managers) == 1
    assert len(test_config.package_managers[0].packages) == 2


def test_config_languages_only():
    test_config = RubricalConfig(
        **{
            "version": 1,
            "languages": [{"name": "python", "warn": "v3.12.0", "block": "v3.10.0"}],
        }
    )

    assert test_config.languages[0].name == "python"
    assert test_config.package_managers == []


def test_config_without_languages():
    test_config = RubricalConfig(**TEST_CONFIG)  # ty: ignore

    assert test_config.languages == []


@pytest.mark.parametrize(
    "languages",
    [
        [{"name": "cobol", "warn": "v1.0.0", "block": "v0.5.0"}],
        [
            {"name": "go", "warn": "v1.22.0", "block": "v1.20.0"},
            {"name": "go", "warn": "v1.23.0", "block": "v1.21.0"},
        ],
    ],
    ids=["unknown-language", "duplicate-language"],
)
def test_config_invalid_languages(languages):
    with pytest.raises(ValidationError):
        RubricalConfig(**{"version": 1, "languages": languages})
