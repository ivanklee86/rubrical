from pathlib import Path
from typing import Dict, List, Tuple

from rubrical.comparisons import check_package
from rubrical.comparisons.lower_bound import compare_language
from rubrical.enum import PackageCheck, SupportedLanguages, SupportedPackageManagers
from rubrical.languages import go as go_language
from rubrical.languages import nodejs as nodejs_language
from rubrical.languages import python as python_language
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.package_managers.go import Go
from rubrical.package_managers.jsonnet import Jsonnet
from rubrical.package_managers.nodejs import NodeJS
from rubrical.package_managers.python import Python
from rubrical.reporters import terminal
from rubrical.schemas.configuration import LanguageRequirement, RubricalConfig
from rubrical.schemas.results import PackageCheckResult
from rubrical.utilities import console

PACKAGE_MANAGER_MAPPING = {
    SupportedPackageManagers.JSONNET.value: Jsonnet,
    SupportedPackageManagers.PYTHON.value: Python,
    SupportedPackageManagers.GO.value: Go,
    SupportedPackageManagers.NODEJS.value: NodeJS,
}

LANGUAGE_MAPPING = {
    SupportedLanguages.PYTHON.value: python_language.Python,
    SupportedLanguages.GO.value: go_language.Go,
    SupportedLanguages.NODEJS.value: nodejs_language.NodeJS,
}

LANGUAGES_REPORT_NAME = "languages"


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
                PACKAGE_MANAGER_MAPPING[package_manager.name]()  #  type:  ignore
            )

    def check_all(
        self,
    ) -> Tuple[bool, bool, Dict[str, List[PackageCheckResult]]]:
        """Grades configured languages, then configured package managers."""
        warnings_found = False
        blocks_found = False
        results: Dict[str, List[PackageCheckResult]] = {}

        # Only report languages when configured, so existing reports are unchanged.
        if self.configuration.languages:
            language_results = self.check_languages()
            terminal.terminal_report(LANGUAGES_REPORT_NAME, language_results)

            warnings_found = any(x.check == PackageCheck.WARN for x in language_results)
            blocks_found = any(x.check == PackageCheck.BLOCK for x in language_results)
            results[LANGUAGES_REPORT_NAME] = language_results

        (
            package_warnings_found,
            package_blocks_found,
            package_results,
        ) = self.check_package_managers()

        return (
            warnings_found or package_warnings_found,
            blocks_found or package_blocks_found,
            results | package_results,
        )

    def check_languages(self) -> List[PackageCheckResult]:
        console.print_header("Grading languages", "🈴")
        check_results: List[PackageCheckResult] = []

        for requirement in self.configuration.languages:
            check_results.extend(self.check_language(requirement))

        return check_results

    def check_language(
        self, requirement: LanguageRequirement
    ) -> List[PackageCheckResult]:
        check_results: List[PackageCheckResult] = []
        language = LANGUAGE_MAPPING[requirement.name]()  # ty: ignore

        language.read_files(self.repository_path)
        language.parse_files()

        if self.debug:
            for file in language.found_files.keys() - language.declarations.keys():
                console.print_debug(
                    f"{file} doesn't declare a {language.name} version."
                )

        for file, declaration in language.declarations.items():
            grade = compare_language(requirement, declaration)

            if self.debug:
                console.print_debug(
                    f"{language.name} @ {declaration.raw_constraint} in {file} is {grade.check.value}: {grade.reason}."
                )

            check_results.append(
                PackageCheckResult(
                    name=language.name,
                    file=file,
                    check=grade.check,
                    version_package=declaration.raw_constraint,
                    version_warn=requirement.warn,
                    version_block=requirement.block,
                )
            )

        return check_results

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
                            f"Checking {package.name} @ {package.raw_constraint}."
                        )

                    if package_manager.normalize_name(
                        package_requirements.name
                    ) == package_manager.normalize_name(package.name):
                        check_results.append(
                            PackageCheckResult(
                                name=package.name,
                                file=file,
                                check=check_package(package_requirements, package),
                                version_package=package.raw_constraint,
                                version_warn=package_requirements.warn,
                                version_block=package_requirements.block,
                            )
                        )
                        if self.debug:
                            console.print_debug(
                                f"Check result for {package.name} @ {package.raw_constraint} is {check_results[-1].check.value}."
                            )

        return check_results
