from dataclasses import dataclass
from pathlib import Path
from typing import List

from rubrical.configuration import RubricalConfig
from rubrical.enum import PackageCheck, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.package_managers.jsonnet import Jsonnet

PACKAGE_MANAGER_MAPPING = {SupportedPackageManagers.JSONNET.value: Jsonnet}


@dataclass
class PackageCheckResult:
    name: str
    file: str
    check: PackageCheck


class Rubrical:
    configuration: RubricalConfig
    package_managers: List[BasePackageManager]
    repository_path: Path

    def __init__(self, configuration: RubricalConfig, repository_path: Path) -> None:
        self.configuration = configuration
        self.repository_path = repository_path
        self.package_managers = []

        for package_manager in self.configuration.package_managers:
            self.package_managers.append(
                PACKAGE_MANAGER_MAPPING[package_manager.name]()
            )

    def check_package_manager(
        self, package_manager: BasePackageManager
    ) -> List[PackageCheckResult]:
        check_results: List[PackageCheckResult] = []

        package_manager.read_package_manager_files(self.repository_path)
        package_manager.parse_package_manager_files()

        [configuration] = [
            x
            for x in self.configuration.package_managers
            if x.name == package_manager.name
        ]

        for package_requirements in configuration.packages:
            for file in package_manager.packages.keys():
                for package in package_manager.packages[file]:
                    if package_requirements.name == package.name:
                        check_results.append(
                            PackageCheckResult(
                                name=package.name,
                                file=file,
                                check=package_requirements.check_package(package),
                            )
                        )

        return check_results
