from pathlib import Path

from rubrical.package_managers.go import Go
from tests.constants import FILES_FOLDER_PATH


def test_go():
    go = Go()

    go.read_package_manager_files(Path(FILES_FOLDER_PATH, "go"))
    go.parse_package_manager_files()

    assert len(go.packages["go.mod"]) == 30
