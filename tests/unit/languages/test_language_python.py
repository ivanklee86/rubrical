from pathlib import Path

from rubrical.enum import VersionDialect
from rubrical.languages.python import Python
from rubrical.utilities.files import FileDetails
from tests.constants import FILES_FOLDER_PATH


def _parse(contents: str):
    return Python().parse_file(
        FileDetails(
            name="pyproject.toml", path=Path("pyproject.toml"), contents=contents
        )
    )


def test_python_fixtures():
    python = Python()
    python.read_files(FILES_FOLDER_PATH)
    python.parse_files()

    declarations = {
        file: (x.version, x.dialect) for file, x in python.declarations.items()
    }

    assert declarations == {
        "python/pyproject.toml": (">=3.7", VersionDialect.PEP440),
        "uv/pyproject.toml": (">=3.14", VersionDialect.PEP440),
        "python-gt/pyproject.toml": (">3.9", VersionDialect.PEP440),
        "poetry/pyproject.toml": ("^3.12", VersionDialect.POETRY),
        "poetry-or/pyproject.toml": (">=3.8 <3.9 || >=3.10", VersionDialect.POETRY),
    }


def test_python_requires_python_wins_over_poetry():
    declaration = _parse(
        '[project]\nrequires-python = ">=3.8"\n\n'
        '[tool.poetry.dependencies]\npython = ">=3.8,<4.0"\n'
    )

    assert declaration
    assert declaration.version == ">=3.8"
    assert declaration.dialect == VersionDialect.PEP440


def test_python_without_declaration():
    assert _parse('[project]\nname = "no-python"\n') is None
    assert _parse('[tool.poetry.dependencies]\nrequests = "^2.31.0"\n') is None


def test_python_skips_virtualenvs(tmp_path):
    venv_package = Path(tmp_path, ".venv", "lib", "package")
    venv_package.mkdir(parents=True)
    Path(venv_package, "pyproject.toml").write_text(
        '[project]\nrequires-python = ">=2.7"\n'
    )

    python = Python()
    python.read_files(tmp_path)
    python.parse_files()

    assert python.declarations == {}
