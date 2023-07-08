import pyproject_parser
import requirements
import tomllib
from requirements.requirement import Requirement

from rubrical.enum import DependencySpecifications, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.schemas.package import Package


class Python(BasePackageManager):
    target_files = ["requirements.txt", "pyproject.toml"]

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedPackageManagers.PYTHON.value

        self.specification_symbols = self.specification_symbols | {
            DependencySpecifications.APPROX_EQ.value: ["~="]
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

    def _parse_requirement(self, req: Requirement, package_file_filename: str):
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

    def parse_package_manager_file(
        self, package_file_filename: str, package_file_contents: str
    ) -> None:
        self.packages[package_file_filename] = []

        if "requirements.txt" in package_file_filename:
            for req in requirements.parse(package_file_contents):
                self._parse_requirement(
                    req=req, package_file_filename=package_file_filename
                )

        elif "pyproject.toml" in package_file_filename:
            pyproject_contents = tomllib.loads(package_file_contents)
            parser = pyproject_parser.PyProject()
            contents = parser.from_dict(pyproject_contents)

            # Is not a Poetry file.
            if contents.project and "dependencies" in contents.project.keys():
                for pyproject_req in contents.project["dependencies"]:
                    # Hacky hack to use same parser as requirements.txt
                    for fake_req in requirements.parse(str(pyproject_req)):
                        self._parse_requirement(fake_req, package_file_filename)
