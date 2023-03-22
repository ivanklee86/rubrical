import json
from pathlib import Path

from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.schemas.package import Package
from tests.constants import FILES_FOLDER_PATH


class TestPackageManager(BasePackageManager):
    target_file = "test.json"

    def parse_package_manager_file(self, package_file_filename: str, package_file: str):
        file_json = json.loads(package_file)

        self.packages[package_file_filename] = []

        for dependency in file_json["dependencies"]:
            self.packages[package_file_filename].append(Package(**dependency))


def test_find_and_load():
    test_manager = TestPackageManager()

    test_manager.read_package_manager_files(Path(FILES_FOLDER_PATH, "dummy"))
    test_manager.parse_package_manager_files()

    assert test_manager.packages
    assert len(test_manager.packages["test.json"]) == 2
    assert type(test_manager.packages["submodule/test.json"][0]) == Package
