from typing import List

import pyproject_parser
import requirements
import tomllib
from requirements.requirement import Requirement
from requirements_detector import find_requirements

from rubrical.enum import DependencySpecifications, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import (
    BasePackageManager,
    PackageManagerFileDetails,
)
from rubrical.schemas.package import Package, Specification


class Python(BasePackageManager):
    target_files = ["requirements.txt", "pyproject.toml"]

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedPackageManagers.PYTHON.value

        self.specification_symbols = self.specification_symbols | {
            DependencySpecifications.APPROX_EQ.value: ["~="]
        }

    def _parse_requirement(self, req: Requirement, package_file_filename: str):
        if req.specifier and req.specs:
            version_constraints: List[Specification] = []

            for spec in req.specs:
                specifier = DependencySpecifications.EQ
                for key, value in self.specification_symbols.items():
                    if spec[0] in value:
                        specifier = DependencySpecifications[key]

                version_constraints.append(
                    Specification(
                        version=spec[1],
                        specifier=specifier,
                    )
                )

            self.append_package(
                package_file_filename,
                Package(
                    name=req.name,
                    raw_constraint=req.line,
                    version_constraints=version_constraints,
                ),
            )

    def parse_package_manager_file(
        self, package_manager_file_details: PackageManagerFileDetails
    ) -> None:
        self.packages[package_manager_file_details.name] = []

        if "requirements.txt" in package_manager_file_details.name:
            for req in requirements.parse(package_manager_file_details.contents):
                self._parse_requirement(
                    req=req, package_file_filename=package_manager_file_details.name
                )

        elif "pyproject.toml" in package_manager_file_details.name:
            pyproject_contents = tomllib.loads(package_manager_file_details.contents)
            parser = pyproject_parser.PyProject()
            contents = parser.from_dict(pyproject_contents)

            # Is not a Poetry file.
            if contents.project and "dependencies" in contents.project.keys():
                for pyproject_req in contents.project["dependencies"]:
                    # Hacky hack to use same parser as requirements.txt
                    for fake_req in requirements.parse(str(pyproject_req)):
                        self._parse_requirement(
                            fake_req, package_manager_file_details.name
                        )
            elif contents.tool and "poetry" in contents.tool.keys():
                poetry_requirements = find_requirements(
                    package_manager_file_details.path.parent
                )
                for poetry_requirement in poetry_requirements:
                    reqs = requirements.parse(str(poetry_requirement))
                    for req in reqs:
                        self._parse_requirement(
                            req=req,
                            package_file_filename=package_manager_file_details.name,
                        )
