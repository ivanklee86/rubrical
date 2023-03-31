import requirements

from rubrical.enum import DependencySpecifications, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.schemas.package import Package


class Python(BasePackageManager):
    target_file = "requirements.txt"

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedPackageManagers.PYTHON.value

        self.specification_symbols = self.specification_symbols | {
            DependencySpecifications.COMPATIBLE.value: ["~="]
        }

    def _set_package(self, package_file_filename: str, requirement, spec):
        for key, value in self.specification_symbols.items():
            if spec[0] in value:
                self.append_package(
                    package_file_filename,
                    Package(
                        name=requirement.name,
                        version=spec[1],
                        specifier=DependencySpecifications(key),
                    ),
                )

    def parse_package_manager_file(
        self, package_file_filename: str, package_file_contents: str
    ) -> None:
        self.packages[package_file_filename] = []

        for req in requirements.parse(package_file_contents):
            if req.specifier:
                # Handle cases for single specifiers.
                if len(req.specs) == 1:
                    [spec] = req.specs
                    self._set_package(package_file_filename, req, spec)
                elif len(req.specs) > 1:
                    [spec] = [
                        x
                        for x in req.specs
                        if x[0]
                        in self.specification_symbols["GT"]
                        + self.specification_symbols["GTE"]
                    ]
                    self._set_package(package_file_filename, req, spec)
                else:
                    pass
