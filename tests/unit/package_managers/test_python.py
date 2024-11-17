from pathlib import Path

from rubrical.enum import DependencySpecifications
from rubrical.package_managers.python import Python
from rubrical.schemas.package import Specification
from tests.constants import FILES_FOLDER_PATH


def test_python():
    python = Python()

    python.read_package_manager_files(Path(FILES_FOLDER_PATH, "python"))
    python.parse_package_manager_files()

    assert len(python.packages["requirements.txt"]) == 6
    assert len(python.packages["pyproject.toml"]) == 2

    # Check single version specifiers.
    [dep] = [x for x in python.packages["requirements.txt"] if x.name == "docopt"]
    assert dep.version_constraints[0].version == "0.6.1"
    assert dep.version_constraints[0].specifier == DependencySpecifications.EQ

    # Check pyproject.toml parsing
    [dep] = [x for x in python.packages["pyproject.toml"] if x.name == "apscheduler"]
    assert dep.version_constraints[0].version == "4.0.0"
    assert dep.version_constraints[0].specifier == DependencySpecifications.LT

    # Check for multiple version specifiers.
    [dep] = [
        x
        for x in python.packages["requirements.txt"]
        if x.name == "something-something"
    ]
    assert (
        Specification(version="1.5", specifier=DependencySpecifications.GT)
        in dep.version_constraints
    )
    assert (
        Specification(version="1.6", specifier=DependencySpecifications.LT)
        in dep.version_constraints
    )


def test_poetry():
    python = Python()

    python.read_package_manager_files(Path(FILES_FOLDER_PATH, "poetry"))
    python.parse_package_manager_files()

    [dep] = [x for x in python.packages["pyproject.toml"] if x.name == "pydantic"]
    assert len(dep.version_constraints) == 2
