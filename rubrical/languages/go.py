import re
from typing import Optional

from rubrical.enum import SupportedLanguages, VersionDialect
from rubrical.languages import version_files
from rubrical.languages.base_language import BaseLanguage
from rubrical.schemas.language import LanguageDeclaration
from rubrical.utilities.files import FileDetails

GO_DIRECTIVE = re.compile(r"^go\s+(\S+)", re.MULTILINE)
# The Go toolchain treats a go.mod without a `go` directive as `go 1.16`.
IMPLICIT_GO_VERSION = "1.16"


class Go(BaseLanguage):
    target_files = ["go.mod", ".go-version"]

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedLanguages.GO.value

    def parse_file(self, file_details: FileDetails) -> Optional[LanguageDeclaration]:
        if file_details.path.name == ".go-version":
            return version_files.declaration(
                file_details.path.name,
                version_files.go_version(file_details.contents),
                VersionDialect.VERSION_FILE,
            )

        # The `toolchain` directive is only a suggestion, so only `go` is graded.
        if match := GO_DIRECTIVE.search(file_details.contents):
            version = match.group(1).strip('"')
            raw_constraint = f"go {version}"
        else:
            version = IMPLICIT_GO_VERSION
            raw_constraint = f"go {version} (implicit)"

        return LanguageDeclaration(
            version=version, raw_constraint=raw_constraint, dialect=VersionDialect.GO
        )
