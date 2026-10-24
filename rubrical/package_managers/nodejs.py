import json
import re
from typing import List

from rubrical.enum import DependencySpecifications, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import (
    BasePackageManager,
    PackageManagerFileDetails,
)
from rubrical.schemas.package import Package, Specification

# node-semver ignores whitespace between an operator and its version, e.g. `>= 1.2.3`.
OPERATOR_WHITESPACE = re.compile(r"(<=|>=|=<|=>|<|>|=|\^|~)\s+")
# Partial versions are X-ranges, e.g. `1`, `1.2`, `1.x`, `1.2.*`, `1.x.x`.
X_RANGE = re.compile(r"^(\d+(?:\.\d+)?)(?:\.[xX*])*$")


class NodeJS(BasePackageManager):
    target_files = ["package.json"]
    denylist_pathnames = ["node_modules"]
    dependency_keys = ["dependencies", "devDependencies", "peerDependencies"]

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedPackageManagers.NODEJS.value

        self.specification_symbols = self.specification_symbols | {
            DependencySpecifications.APPROX_EQ.value: ["~"],
            DependencySpecifications.COMPATIBLE.value: ["^"],
        }

    def _parse_packagelock(
        self, package_manager_file_details: PackageManagerFileDetails
    ):
        self.packages[package_manager_file_details.name] = []
        package_json = json.loads(package_manager_file_details.contents)

        for dependency_key in [
            x for x in package_json.keys() if x in self.dependency_keys
        ]:
            dependency_section = package_json[dependency_key]

            for package, raw_version in dependency_section.items():
                version = OPERATOR_WHITESPACE.sub(r"\1", raw_version.strip())

                if " " not in version:  # Handle most cases through symbol matching
                    if x_range := X_RANGE.match(version):  # Handle 1, 1.2, 1.2.x
                        self.packages[package_manager_file_details.name].append(
                            Package(
                                name=package,
                                raw_constraint=f"{package} {raw_version}",
                                version_constraints=[
                                    Specification(
                                        version=x_range.group(1),
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
                        self.packages[package_manager_file_details.name].append(
                            Package(
                                name=package,
                                raw_constraint=f"{package} {raw_version}",
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
                    self.packages[package_manager_file_details.name].append(
                        Package(
                            name=package,
                            raw_constraint=f"{package} {raw_version}",
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

                        self.packages[package_manager_file_details.name].append(
                            Package(
                                name=package,
                                raw_constraint=f"{package} {raw_version}",
                                version_constraints=version_constraints,
                            )
                        )

    def parse_package_manager_file(
        self, package_manager_file_details: PackageManagerFileDetails
    ) -> None:
        if "package.json" in package_manager_file_details.name:
            self._parse_packagelock(package_manager_file_details)
