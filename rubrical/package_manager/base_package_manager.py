import abc
from pathlib import Path
from typing import Dict, List

from rubrical.dependency import Dependency


class BasePackageManager(abc.ABC):
    target_file: str = ""
    found_files: Dict[str, str] = {}
    dependencies: Dict[str, List[Dependency]] = {}

    def read_dependency_files(self, current_folder: Path):
        dependency_files = current_folder.rglob(self.target_file)

        for dependency_file in dependency_files:
            with open(str(dependency_file), "r") as file:
                self.found_files[
                    str(dependency_file.relative_to(current_folder))
                ] = file.read()

    def parse_dependency_files(self):
        for file in self.found_files.items():
            self.parse_dependency_file(*file)

    @abc.abstractmethod
    def parse_dependency_file(self, dependency_filename: str, dependency_file: str):
        pass
