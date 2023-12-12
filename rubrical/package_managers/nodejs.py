import json
from typing import List

from rubrical.enum import DependencySpecifications, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.schemas.package import Package, Specification


class NodeJS(BasePackageManager):
    target_files = ["package.json"]

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedPackageManagers.NODEJS.value

        self.specification_symbols = self.specification_symbols | {
            DependencySpecifications.APPROX_EQ.value: ["~"],
            DependencySpecifications.COMPATIBLE.value: ["^"],
        }

    def _parse_packagelock(
        self, package_file_filename: str, package_file_contents: str
    ):
        self.packages[package_file_filename] = []
        package_json = json.loads(package_file_contents)

        for dependency_key in [
            x for x in package_json.keys() if "dependencies" in x.lower()
        ]:
            dependency_section = package_json[dependency_key]

            for package, version in dependency_section.items():
                if " " not in version:  # Handle most cases through symbol matching
                    if version[-2:] == ".x":  # Handle 1.2.x
                        self.packages[package_file_filename].append(
                            Package(
                                name=package,
                                raw_constraint=f"{package} {version}",
                                version_constraints=[
                                    Specification(
                                        version=version[:-2],
                                        specifier=DependencySpecifications.APPROX_EQ,
                                    )
                                ],
                            )
                        )
                    else:
                        (
                            specifier,
                            sanitized_version,
                        ) = self.match_from_specification_symbols(version)
                        self.packages[package_file_filename].append(
                            Package(
                                name=package,
                                raw_constraint=f"{package} {version}",
                                version_constraints=[
                                    Specification(
                                        version=sanitized_version, specifier=specifier
                                    )
                                ],
                            )
                        )
                elif (
                    "||" in version
                ):  # Not sure if we can programatically parse this. :'(
                    pass
                elif "-" in version:  # Handle range
                    range_versions = [x.strip(" ") for x in version.split("-")]
                    self.packages[package_file_filename].append(
                        Package(
                            name=package,
                            raw_constraint=f"{package} {version}",
                            version_constraints=[
                                Specification(
                                    version=range_versions[0],
                                    specifier=DependencySpecifications.GTE,
                                ),
                                Specification(
                                    version=range_versions[1],
                                    specifier=DependencySpecifications.LTE,
                                ),
                            ],
                        )
                    )
                else:  # Handle standard range based definitions
                    range_versions = version.split(" ")
                    if len(range_versions) != 2:
                        pass  # Tomfoolery
                    else:
                        version_constraints: List[Specification] = []

                        for parsed_version in range_versions:
                            (
                                specifier,
                                sanitized_version,
                            ) = self.match_from_specification_symbols(parsed_version)

                            version_constraints.append(
                                Specification(
                                    version=sanitized_version,
                                    specifier=specifier,
                                )
                            )

                        self.packages[package_file_filename].append(
                            Package(
                                name=package,
                                raw_constraint=f"{package} {version}",
                                version_constraints=version_constraints,
                            )
                        )

    def parse_package_manager_file(
        self, package_file_filename: str, package_file_contents: str
    ) -> None:
        if "package.json" in package_file_filename:
            self._parse_packagelock(package_file_filename, package_file_contents)
