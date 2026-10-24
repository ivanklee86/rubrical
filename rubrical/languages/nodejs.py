import json
from typing import Optional

from rubrical.enum import SupportedLanguages, VersionDialect
from rubrical.languages.base_language import BaseLanguage
from rubrical.schemas.language import LanguageDeclaration
from rubrical.utilities.files import FileDetails


class NodeJS(BaseLanguage):
    target_files = ["package.json"]
    denylist_pathnames = ["node_modules"]

    def __init__(self) -> None:
        super().__init__()

        self.name = SupportedLanguages.NODEJS.value

    def parse_file(self, file_details: FileDetails) -> Optional[LanguageDeclaration]:
        engines = json.loads(file_details.contents).get("engines")
        node = engines.get("node") if isinstance(engines, dict) else None

        if isinstance(node, str):
            return LanguageDeclaration(
                version=node,
                raw_constraint=f'engines.node "{node}"',
                dialect=VersionDialect.NPM,
            )

        return None
