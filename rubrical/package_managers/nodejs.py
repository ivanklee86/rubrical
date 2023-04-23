import json

from benedict import benedict

from rubrical.enum import DependencySpecifications, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.schemas.package import Package


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
        package_json = benedict(json.loads(package_file_contents))

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
                                version=version[:-2],
                                specifier=DependencySpecifications.APPROX_EQ,
                            )
                        )
                    else:
                        (
                            specier,
                            sanitized_version,
                        ) = self.match_from_specification_symbols(version)
                        self.packages[package_file_filename].append(
                            Package(
                                name=package,
                                version=sanitized_version,
                                specifier=specier,
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
                            version=range_versions[0],
                            specifier=DependencySpecifications.GTE,
                        )
                    )
                else:  # Handle standard range based definitions
                    range_versions = version.split(" ")
                    if len(range_versions) != 2:
                        pass  # Tomfoolery
                    else:
                        [lower_bound_version] = [
                            x
                            for x in range_versions
                            if any(
                                symbol in x
                                for symbol in self.specification_symbols["GT"]
                                + self.specification_symbols["GTE"]
                            )
                        ]
                        (
                            specier,
                            sanitized_version,
                        ) = self.match_from_specification_symbols(lower_bound_version)
                        self.packages[package_file_filename].append(
                            Package(
                                name=package,
                                version=sanitized_version,
                                specifier=specier,
                            )
                        )

    def parse_package_manager_file(
        self, package_file_filename: str, package_file_contents: str
    ) -> None:
        if "package.json" in package_file_filename:
            self._parse_packagelock(package_file_filename, package_file_contents)
