import abc
from pathlib import Path
from typing import Dict, List

from rubrical.package import Package


class BasePackageManager(abc.ABC):
    name: str = ""
    target_file: str = ""
    found_files: Dict[str, str]
    packages: Dict[str, List[Package]]

    def __init__(self) -> None:
        super().__init__()

        self.found_files = {}
        self.packages = {}

    def read_package_manager_files(self, current_folder: Path):
        package_manager_files = current_folder.rglob(self.target_file)

        for package_manager_file in package_manager_files:
            with open(str(package_manager_file), "r") as file:
                self.found_files[
                    str(package_manager_file.relative_to(current_folder))
                ] = file.read()

    def parse_package_manager_files(self):
        for file in self.found_files.items():
            self.parse_package_manager_file(*file)

    @abc.abstractmethod
    def parse_package_manager_file(self, package_file_filename: str, package_file: str):
        pass
