import json

from rubrical.dependency import Dependency
from rubrical.package_manager.base_package_manager import BasePackageManager


class TestPackageManager(BasePackageManager):
    target_file = "test.json"

    def parse_dependency_file(self, dependency_filename: str, dependency_file: str):
        file_json = json.loads(dependency_file)

        self.dependencies[dependency_filename] = []

        for dependency in file_json["dependencies"]:
            self.dependencies[dependency_filename].append(Dependency(**dependency))
