# ruff: noqa: PLR2004
from rubrical.configuration.rubrical_config import RubricalConfig

TEST_CONFIG = {
    "version": 1,
    "dependency_managers": [
        {
            "name": "jsonnet",
            "dependencies": [
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
    test_config = RubricalConfig(**TEST_CONFIG)
    assert len(test_config.dependency_managers) == 1
    assert len(test_config.dependency_managers[0].dependencies) == 2
