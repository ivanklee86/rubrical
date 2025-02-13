import abc
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from rubrical.enum import DependencySpecifications
from rubrical.schemas.package import Package


@dataclass
class PackageManagerFileDetails:
    name: str
    path: Path
    contents: str


class BasePackageManager(abc.ABC):
    name: str = ""
    target_files: List[str] = []
    denylist_pathnames: List[str] = []
    found_files: Dict[str, PackageManagerFileDetails]
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
            if self.denylist_pathnames and any(
                x in str(package_manager_file) for x in self.denylist_pathnames
            ):
                pass
            else:
                with open(str(package_manager_file), "r") as file:
                    file_name = str(package_manager_file.relative_to(current_folder))

                    self.found_files[file_name] = PackageManagerFileDetails(
                        name=file_name, path=package_manager_file, contents=file.read()
                    )

    def parse_package_manager_files(self):
        for file in self.found_files.values():
            self.parse_package_manager_file(file)

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
        self, package_manager_file_details: PackageManagerFileDetails
    ) -> None:
        pass
