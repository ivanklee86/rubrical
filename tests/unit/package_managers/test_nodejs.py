from pathlib import Path

from rubrical.enum import DependencySpecifications
from rubrical.package_managers.nodejs import NodeJS
from tests.constants import FILES_FOLDER_PATH


def test_nodejs():
    nodejs = NodeJS()

    nodejs.read_package_manager_files(Path(FILES_FOLDER_PATH, "nodejs"))
    nodejs.parse_package_manager_files()

    assert len(nodejs.packages["package.json"]) == 104
    assert len(nodejs.packages["complex/package.json"]) == 11

    # Check single version specifiers.
    [dep] = [x for x in nodejs.packages["complex/package.json"] if x.name == "til"]
    assert dep.version == "1.2"
    assert dep.specifier == DependencySpecifications.APPROX_EQ

    # Check for multiple version specifiers in dash-based ranges
    [dep] = [x for x in nodejs.packages["complex/package.json"] if x.name == "foo"]
    assert dep.version == "1.0.0"
    assert dep.specifier == DependencySpecifications.GTE

    # Check for multiple version specifiers in dash-based ranges
    [dep] = [x for x in nodejs.packages["complex/package.json"] if x.name == "baz"]
    assert dep.version == "1.0.2"
    assert dep.specifier == DependencySpecifications.GT
