import abc
from pathlib import Path
from typing import Dict, List, Tuple

from rubrical.enum import DependencySpecifications
from rubrical.schemas.package import Package


class BasePackageManager(abc.ABC):
    name: str = ""
    target_files: List[str] = []
    found_files: Dict[str, str]
    packages: Dict[str, List[Package]]
    specification_symbols: Dict[str, List[str]] = {
        DependencySpecifications.EQ.value: ["=="],
        DependencySpecifications.GT.value: [">"],
        DependencySpecifications.GTE.value: [">=", "=>"],
        DependencySpecifications.LT.value: ["<"],
        DependencySpecifications.LTE.value: ["<=", "=<"],
        DependencySpecifications.NE.value: ["!="],
        DependencySpecifications.COMPATIBLE.value: [],
        DependencySpecifications.APPROX_EQ.value: [],
    }

    def __init__(self) -> None:
        super().__init__()

        self.found_files = {}
        self.packages = {}

    def read_package_manager_files(self, current_folder: Path):
        package_manager_files: List[Path] = []

        for target_file in self.target_files:
            package_manager_files.extend(current_folder.rglob(target_file))

        for package_manager_file in package_manager_files:
            with open(str(package_manager_file), "r") as file:
                self.found_files[
                    str(package_manager_file.relative_to(current_folder))
                ] = file.read()

    def parse_package_manager_files(self):
        for file in self.found_files.items():
            self.parse_package_manager_file(*file)

    def append_package(self, package_file_filename: str, package: Package):
        self.packages[package_file_filename].append(package)

    def match_from_specification_symbols(
        self, version: str
    ) -> Tuple[DependencySpecifications, str]:
        specficiation = DependencySpecifications.EQ
        sanitized_version = version

        for key, specification_symbols in self.specification_symbols.items():
            if any(symbol in version for symbol in specification_symbols):
                specficiation = DependencySpecifications[key]

                for symbol in specification_symbols:
                    for symbol_char in symbol:
                        sanitized_version = sanitized_version.replace(symbol_char, "")

        return (specficiation, sanitized_version)

    @abc.abstractmethod
    def parse_package_manager_file(
        self, package_file_filename: str, package_file_contents: str
    ) -> None:
        pass
