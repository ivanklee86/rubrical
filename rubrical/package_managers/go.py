import re

from rubrical.enum import DependencySpecifications, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import (
    BasePackageManager,
    PackageManagerFileDetails,
)
from rubrical.schemas.package import Package, Specification


class Go(BasePackageManager):
    target_files = ["go.mod"]

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedPackageManagers.GO.value

    def parse_package_manager_file(
        self, package_manager_file_details: PackageManagerFileDetails
    ) -> None:
        self.packages[package_manager_file_details.name] = []
        modules = []

        go_import_regex = re.compile("\\(([^)]+)\\)")
        matched_groups = go_import_regex.findall(package_manager_file_details.contents)
        for group in matched_groups:
            lines = group.split("\n")
            modules.extend(
                [x.replace("\t", "") for x in lines if x and "indirect" not in x]
            )

        for module in modules:
            module_specs = module.split(" ")

            self.packages[package_manager_file_details.name].append(
                Package(
                    name=module_specs[0],
                    raw_constraint=module,
                    version_constraints=[
                        Specification(
                            version=module_specs[1],
                            specifier=DependencySpecifications.EQ,
                        )
                    ],
                )
            )
