from pathlib import Path

from rubrical.enum import VersionDialect
from rubrical.languages.go import Go
from rubrical.utilities.files import FileDetails
from tests.constants import FILES_FOLDER_PATH


def _declarations(folder: str):
    go = Go()
    go.read_files(Path(FILES_FOLDER_PATH, folder))
    go.parse_files()

    return go.declarations


def test_go_directive():
    [declaration] = _declarations("go").values()

    assert declaration.version == "1.19"
    assert declaration.raw_constraint == "go 1.19"
    assert declaration.dialect == VersionDialect.GO


def test_go_ignores_toolchain_directive():
    declaration = _declarations("go-toolchain")["go.mod"]

    assert declaration.version == "1.21rc1"


def test_go_missing_directive_is_implicit_1_16():
    declaration = _declarations("go-implicit")["go.mod"]

    assert declaration.version == "1.16"
    assert declaration.raw_constraint == "go 1.16 (implicit)"


def test_go_ignores_module_paths_starting_with_go():
    contents = (
        "module go.example.com/mod\n\ngo 1.22.0\n\nrequire go.uber.org/zap v1.27.0\n"
    )

    declaration = Go().parse_file(
        FileDetails(name="go.mod", path=Path("go.mod"), contents=contents)
    )

    assert declaration
    assert declaration.version == "1.22.0"
