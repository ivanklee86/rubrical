import json
from pathlib import Path

from rubrical.enum import DependencySpecifications
from rubrical.package_managers.base_package_manager import (
    BasePackageManager,
    PackageManagerFileDetails,
)
from rubrical.schemas.package import Package, Specification
from tests.constants import FILES_FOLDER_PATH


class TestPackageManager(BasePackageManager):
    target_files = ["test.json"]

    def parse_package_manager_file(
        self, package_manager_file_details: PackageManagerFileDetails
    ):
        file_json = json.loads(package_manager_file_details.contents)

        self.packages[package_manager_file_details.name] = []

        for dependency in file_json["dependencies"]:
            self.packages[package_manager_file_details.name].append(
                Package(
                    name=dependency["name"],
                    raw_constraint="",
                    version_constraints=[
                        Specification(
                            version=dependency["version"],
                            specifier=DependencySpecifications.EQ,
                        )
                    ],
                )
            )


def test_find_and_load():
    test_manager = TestPackageManager()

    test_manager.read_package_manager_files(Path(FILES_FOLDER_PATH, "dummy"))
    test_manager.parse_package_manager_files()

    assert test_manager.packages
    assert len(test_manager.packages["test.json"]) == 2
    assert type(test_manager.packages["submodule/test.json"][0]) is Package
