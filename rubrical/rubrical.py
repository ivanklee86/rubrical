from pathlib import Path
from typing import Dict, List, Tuple

from rubrical.comparisons import check_package
from rubrical.enum import PackageCheck, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.package_managers.jsonnet import Jsonnet
from rubrical.package_managers.python import Python
from rubrical.reporters import terminal
from rubrical.schemas.configuration import RubricalConfig
from rubrical.schemas.results import PackageCheckResult
from rubrical.utilities import console

PACKAGE_MANAGER_MAPPING = {
    SupportedPackageManagers.JSONNET.value: Jsonnet,
    SupportedPackageManagers.PYTHON.value: Python,
}


class Rubrical:
    configuration: RubricalConfig
    package_managers: List[BasePackageManager]
    repository_path: Path
    debug: bool

    def __init__(
        self, configuration: RubricalConfig, repository_path: Path, debug: bool = False
    ) -> None:
        self.configuration = configuration
        self.repository_path = repository_path
        self.debug = debug
        self.package_managers = []

        for package_manager in self.configuration.package_managers:
            self.package_managers.append(
                PACKAGE_MANAGER_MAPPING[package_manager.name]()
            )

    def check_package_managers(
        self,
    ) -> Tuple[bool, bool, Dict[str, List[PackageCheckResult]]]:
        warnings_found = False
        blocks_found = False
        results: Dict[str, List[PackageCheckResult]] = {}

        for package_manager in self.package_managers:
            check_results = self.check_package_manager(package_manager)
            terminal.terminal_report(package_manager.name, check_results)

            if (
                any([x.check == PackageCheck.BLOCK for x in check_results])
                and not blocks_found
            ):
                blocks_found = True

            if (
                any([x.check == PackageCheck.WARN for x in check_results])
                and not warnings_found
            ):
                warnings_found = True

            results[package_manager.name] = check_results

        return (warnings_found, blocks_found, results)

    def check_package_manager(
        self, package_manager: BasePackageManager
    ) -> List[PackageCheckResult]:
        console.print_header(f"Grading {package_manager.name}", "🈴")
        check_results: List[PackageCheckResult] = []

        package_manager.read_package_manager_files(self.repository_path)
        package_manager.parse_package_manager_files()

        [configuration] = [
            x
            for x in self.configuration.package_managers
            if x.name == package_manager.name
        ]

        for file in package_manager.packages.keys():
            if self.debug:
                console.print_debug(f"Processing {file}.")

            for package in package_manager.packages[file]:
                for package_requirements in configuration.packages:
                    if self.debug:
                        console.print_debug(
                            f"Checking {package.name} @ {package.version}."
                        )

                    if package_requirements.name == package.name:
                        check_results.append(
                            PackageCheckResult(
                                name=package.name,
                                file=file,
                                check=check_package(package_requirements, package),
                                version_package=package.version,
                                version_warn=package_requirements.warn,
                                version_block=package_requirements.block,
                            )
                        )
                        if self.debug:
                            console.print_debug(
                                f"Check result for {package.name} @ {package.version} is {check_results[-1].check.value}."
                            )

        return check_results
