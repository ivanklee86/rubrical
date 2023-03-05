import json
from typing import List

from pydantic import BaseModel

from rubrical.dependency import Dependency
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.package_managers.utilities import git


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

    def parse_dependency_file(self, dependency_filename: str, dependency_file: str):
        file_contents = json.loads(dependency_file)
        self.dependencies[dependency_filename] = []

        jsonnet_file = JsonnetFile(**file_contents)

        for dependency in jsonnet_file.dependencies:
            self.dependencies[dependency_filename].append(
                Dependency(
                    name=git.repository_from_url(dependency.source.git.remote),
                    version=dependency.version,
                )
            )
