# ruff: noqa: PLR2004
from pathlib import Path

from rubrical.configuration import RubricalConfig
from rubrical.enum import PackageCheck
from rubrical.rubrical import Rubrical
from tests.constants import FILES_FOLDER_PATH

TEST_CONFIG = {
    "version": 1,
    "package_managers": [
        {
            "name": "jsonnet",
            "packages": [
                {"name": "xunleii/vector_jsonnet", "warn": "v0.1.2", "block": "v0.1.0"},
                {
                    "name": "jsonnet-libs/argo-workflows-libsonnet",
                    "warn": "v1.1.3",
                    "block": "v1.1.1",
                },
            ],
        }
    ],
}

TEST_JSONNET_FOLDER = Path(FILES_FOLDER_PATH, "jsonnet")


def test_rubrical_single():
    test_config = RubricalConfig(**TEST_CONFIG)

    rubrical = Rubrical(test_config, TEST_JSONNET_FOLDER)

    result = rubrical.check_package_manager(rubrical.package_managers[0])

    assert len(result) == 2
    [dependency_one] = [x for x in result if x.name == "xunleii/vector_jsonnet"]
    assert dependency_one.check == PackageCheck.WARN
    [dependency_two] = [
        x for x in result if x.name == "jsonnet-libs/argo-workflows-libsonnet"
    ]
    assert dependency_two.check == PackageCheck.BLOCK
