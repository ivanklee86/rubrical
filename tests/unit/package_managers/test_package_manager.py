import json
from pathlib import Path

from rubrical.dependency import Dependency
from rubrical.package_managers.base_package_manager import BasePackageManager
from tests.constants import FILES_FOLDER_PATH


class TestPackageManager(BasePackageManager):
    target_file = "test.json"

    def parse_dependency_file(self, dependency_filename: str, dependency_file: str):
        file_json = json.loads(dependency_file)

        self.dependencies[dependency_filename] = []

        for dependency in file_json["dependencies"]:
            self.dependencies[dependency_filename].append(Dependency(**dependency))


def test_find_and_load():
    test_manager = TestPackageManager()

    test_manager.read_dependency_files(Path(FILES_FOLDER_PATH, "dummy"))
    test_manager.parse_dependency_files()

    assert test_manager.dependencies
    assert len(test_manager.dependencies["test.json"]) == 2
    assert type(test_manager.dependencies["submodule/test.json"][0]) == Dependency
