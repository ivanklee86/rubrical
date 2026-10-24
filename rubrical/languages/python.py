import tomllib
from typing import Optional

from rubrical.enum import SupportedLanguages, VersionDialect
from rubrical.languages import version_files
from rubrical.languages.base_language import BaseLanguage
from rubrical.schemas.language import LanguageDeclaration
from rubrical.utilities.files import FileDetails


class Python(BaseLanguage):
    target_files = ["pyproject.toml", ".python-version"]
    denylist_pathnames = [".venv", "node_modules"]

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedLanguages.PYTHON.value

    def parse_file(self, file_details: FileDetails) -> Optional[LanguageDeclaration]:
        if file_details.path.name == ".python-version":
            return version_files.declaration(
                file_details.path.name,
                version_files.python_version(file_details.contents),
                VersionDialect.PYTHON_VERSION_FILE,
            )

        pyproject = tomllib.loads(file_details.contents)

        # Poetry's `python` must be a subset of `requires-python`, so `requires-python` is the real minimum.
        requires_python = pyproject.get("project", {}).get("requires-python")
        if isinstance(requires_python, str):
            return LanguageDeclaration(
                version=requires_python,
                raw_constraint=f'requires-python "{requires_python}"',
                dialect=VersionDialect.PEP440,
            )

        poetry_python = (
            pyproject.get("tool", {})
            .get("poetry", {})
            .get("dependencies", {})
            .get("python")
        )
        if isinstance(poetry_python, str):
            return LanguageDeclaration(
                version=poetry_python,
                raw_constraint=f'tool.poetry python "{poetry_python}"',
                dialect=VersionDialect.POETRY,
            )

        return None
