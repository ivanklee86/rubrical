import aenum
import requirements

from rubrical.enum import SupportedPackageManagers
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.schemas.package import Package


class Python(BasePackageManager):
    target_file = "requirements.txt"

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedPackageManagers.PYTHON.value
        aenum.extend_enum(self.dependency_specifications, "COMPATIBLE", "~=")
        aenum.extend_enum(self.dependency_specifications, "EXCLUDE", "!=")

    def parse_package_manager_file(
        self, package_file_filename: str, package_file_contents: str
    ) -> None:
        self.packages[package_file_filename] = []

        for req in requirements.parse(package_file_contents):
            if req.specifier:
                # Handle cases for single specifiers.
                if len(req.specs) == 1:
                    [spec] = req.specs
                    if spec[0] in [x.value for x in self.dependency_specifications]:
                        self.append_package(
                            package_file_filename,
                            Package(
                                name=req.name,
                                version=spec[1],
                                specifier=self.dependency_specifications(spec[0]),
                            ),
                        )
                elif len(req.specs) > 1:
                    [spec] = [
                        x
                        for x in req.specs
                        if x[0]
                        in [
                            self.dependency_specifications.GT.value,
                            self.dependency_specifications.GTE.value,
                        ]
                    ]
                    self.append_package(
                        package_file_filename,
                        Package(
                            name=req.name,
                            version=spec[1],
                            specifier=self.dependency_specifications(spec[0]),
                        ),
                    )
                else:
                    pass
