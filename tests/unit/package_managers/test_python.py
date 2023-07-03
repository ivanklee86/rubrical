from pathlib import Path

from rubrical.enum import DependencySpecifications
from rubrical.package_managers.python import Python
from tests.constants import FILES_FOLDER_PATH


def test_python():
    python = Python()

    python.read_package_manager_files(Path(FILES_FOLDER_PATH, "python"))
    python.parse_package_manager_files()

    assert len(python.packages["requirements.txt"]) == 5
    assert len(python.packages["pyproject.toml"]) == 2

    # Check single version specifiers.
    [dep] = [x for x in python.packages["requirements.txt"] if x.name == "docopt"]
    assert dep.version == "0.6.1"
    assert dep.specifier == DependencySpecifications.EQ

    # Check pyproject.toml parsing
    [dep] = [x for x in python.packages["pyproject.toml"] if x.name == "apscheduler"]
    assert dep.version == "4.0.0"
    assert dep.specifier == DependencySpecifications.LT

    # Check for multiple version specifiers.
    [dep] = [
        x
        for x in python.packages["requirements.txt"]
        if x.name == "something-something"
    ]
    assert dep.version == "1.5"
    assert dep.specifier == DependencySpecifications.GT
