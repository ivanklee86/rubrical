from pathlib import Path

from rubrical.enum import VersionDialect
from rubrical.languages.go import Go
from rubrical.languages.nodejs import NodeJS
from rubrical.languages.python import Python
from rubrical.utilities.files import FileDetails
from tests.constants import FILES_FOLDER_PATH


def _parse(language, file_name: str, contents: str):
    return language.parse_file(
        FileDetails(name=file_name, path=Path(file_name), contents=contents)
    )


def test_python_version_keeps_every_line():
    declaration = _parse(
        Python(), ".python-version", "# Tested against both.\n\n  3.12.4  \n3.9\n"
    )

    assert declaration
    assert declaration.version == "3.12.4\n3.9"
    assert declaration.raw_constraint == '.python-version "3.12.4" "3.9"'
    assert declaration.dialect == VersionDialect.PYTHON_VERSION_FILE


def test_python_version_keeps_whole_line():
    # uv parses the whole line, so a specifier set or trailing text is kept as written.
    declaration = _parse(Python(), ".python-version", ">=3.11, <3.13\n")

    assert declaration
    assert declaration.version == ">=3.11, <3.13"


def test_go_version_keeps_first_word_of_each_line():
    declaration = _parse(Go(), ".go-version", "# Pinned.\n1.22.0 primary\n1.21.5\n")

    assert declaration
    assert declaration.version == "1.22.0\n1.21.5"
    assert declaration.dialect == VersionDialect.VERSION_FILE


def test_node_version_keeps_first_word_of_file():
    declaration = _parse(NodeJS(), ".node-version", "v18.17.1 extra\n20\n")

    assert declaration
    assert declaration.version == "v18.17.1"
    assert declaration.raw_constraint == '.node-version "v18.17.1"'
    assert declaration.dialect == VersionDialect.VERSION_FILE


def test_nvmrc_strips_comments_and_key_value_lines():
    declaration = _parse(
        NodeJS(), ".nvmrc", "# Current LTS.\n  20 # LTS\nfuture-key = value\n"
    )

    assert declaration
    assert declaration.version == "20"
    assert declaration.dialect == VersionDialect.VERSION_FILE


def test_nvmrc_keeps_several_versions_together():
    # nvm rejects more than one version, so they stay one ungradeable value.
    declaration = _parse(NodeJS(), ".nvmrc", "20\n18\n")

    assert declaration
    assert declaration.version == "20 18"


def test_version_files_without_versions_produce_no_declaration():
    assert _parse(Python(), ".python-version", "# Nothing pinned.\n\n") is None
    assert _parse(Go(), ".go-version", "") is None
    assert _parse(NodeJS(), ".node-version", "  \n") is None
    assert _parse(NodeJS(), ".nvmrc", "# Comment.\nkey=value\n") is None


def test_version_file_fixtures():
    found = {}
    for language in (Python(), Go(), NodeJS()):
        language.read_files(Path(FILES_FOLDER_PATH, "version-files"))
        language.parse_files()
        found.update({f: x.version for f, x in language.declarations.items()})

    assert found == {
        "python/.python-version": "3.12",
        "python-multi/.python-version": "3.12.4\n3.9",
        "python-specifier/.python-version": ">=3.11, <3.13",
        "python-pypy/.python-version": "pypy3.10",
        "python-system/.python-version": "3.12\nsystem",
        "go/.go-version": "1.21.5",
        "node/.node-version": "v18.17.1",
        "nvmrc/.nvmrc": "20",
        "nvmrc-lts/.nvmrc": "lts/*",
    }
