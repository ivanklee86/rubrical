import json
from typing import List

from pydantic import BaseModel

from rubrical.enum import DependencySpecifications, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.package_managers.utilities import git
from rubrical.schemas.package import Package


class JsonnetDependencySourceGit(BaseModel):
    remote: str
    subdir: str


class JsonnetDependencySource(BaseModel):
    git: JsonnetDependencySourceGit


class JsonnetDependency(BaseModel):
    source: JsonnetDependencySource
    version: str


class JsonnetFile(BaseModel):
    dependencies: List[JsonnetDependency]


class Jsonnet(BasePackageManager):
    target_file = "jsonnetfile.json"

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedPackageManagers.JSONNET.value

    def parse_package_manager_file(
        self, package_file_filename: str, package_file_contents: str
    ) -> None:
        file_contents = json.loads(package_file_contents)
        self.packages[package_file_filename] = []

        jsonnet_file = JsonnetFile(**file_contents)

        for dependency in jsonnet_file.dependencies:
            self.packages[package_file_filename].append(
                Package(
                    name=git.repository_from_url(dependency.source.git.remote),
                    version=dependency.version,
                    specifier=DependencySpecifications.EQ,
                )
            )
