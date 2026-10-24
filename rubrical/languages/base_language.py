import abc
from pathlib import Path
from typing import Dict, List, Optional

from rubrical.schemas.language import LanguageDeclaration
from rubrical.utilities.files import FileDetails, find_files


class BaseLanguage(abc.ABC):
    name: str = ""
    target_files: List[str] = []
    denylist_pathnames: List[str] = []
    found_files: Dict[str, FileDetails]
    declarations: Dict[str, LanguageDeclaration]

    def __init__(self) -> None:
        super().__init__()

        self.found_files = {}
        self.declarations = {}

    def read_files(self, current_folder: Path):
        self.found_files.update(
            find_files(current_folder, self.target_files, self.denylist_pathnames)
        )

    def parse_files(self):
        for file in self.found_files.values():
            declaration = self.parse_file(file)

            # Files that don't declare a version aren't graded.
            if declaration:
                self.declarations[file.name] = declaration

    @abc.abstractmethod
    def parse_file(self, file_details: FileDetails) -> Optional[LanguageDeclaration]:
        pass
