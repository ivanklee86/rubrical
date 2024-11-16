import json
from typing import List, Optional

from pydantic import BaseModel

from rubrical.enum import DependencySpecifications, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import (
    BasePackageManager,
    PackageManagerFileDetails,
)
from rubrical.package_managers.utilities import git
from rubrical.schemas.package import Package, Specification


class JsonnetDependencySourceGit(BaseModel):
    remote: str
    subdir: Optional[str] = ""


class JsonnetDependencySource(BaseModel):
    git: JsonnetDependencySourceGit


class JsonnetDependency(BaseModel):
    source: JsonnetDependencySource
    version: str


class JsonnetFile(BaseModel):
    dependencies: List[JsonnetDependency]


class Jsonnet(BasePackageManager):
    target_files = ["jsonnetfile.json"]

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedPackageManagers.JSONNET.value

    def parse_package_manager_file(
        self, package_manager_file_details: PackageManagerFileDetails
    ) -> None:
        file_contents = json.loads(package_manager_file_details.contents)
        self.packages[package_manager_file_details.name] = []

        jsonnet_file = JsonnetFile(**file_contents)

        for dependency in jsonnet_file.dependencies:
            self.packages[package_manager_file_details.name].append(
                Package(
                    name=git.repository_from_url(dependency.source.git.remote),
                    raw_constraint=f"{git.repository_from_url(dependency.source.git.remote)} {dependency.version}",
                    version_constraints=[
                        Specification(
                            version=dependency.version,
                            specifier=DependencySpecifications.EQ,
                        )
                    ],
                )
            )
