from pathlib import Path

from rubrical.dependency import Dependency
from tests.constants import FILES_FOLDER_PATH
from tests.unit.utilities.dummy_package_manager import TestPackageManager


def test_find_and_load():
    test_manager = TestPackageManager()

    test_manager.read_dependency_files(Path(FILES_FOLDER_PATH, "dummy"))
    test_manager.parse_dependency_files()

    assert test_manager.dependencies
    assert len(test_manager.dependencies["test.json"]) == 2
    assert type(test_manager.dependencies["submodule/test.json"][0]) == Dependency
