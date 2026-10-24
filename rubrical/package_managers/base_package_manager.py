import abc
from pathlib import Path
from typing import Dict, List, Tuple

from rubrical.enum import DependencySpecifications
from rubrical.schemas.package import Package
from rubrical.utilities.files import FileDetails, find_files

# Kept for existing imports; package manager and language files share FileDetails.
PackageManagerFileDetails = FileDetails


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
        self.found_files.update(
            find_files(current_folder, self.target_files, self.denylist_pathnames)
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

    def normalize_name(self, name: str) -> str:
        return name

    @abc.abstractmethod
    def parse_package_manager_file(
        self, package_manager_file_details: PackageManagerFileDetails
    ) -> None:
        pass
