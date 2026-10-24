from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class FileDetails:
    name: str
    path: Path
    contents: str


def find_files(
    current_folder: Path, target_files: List[str], denylist_pathnames: List[str]
) -> Dict[str, FileDetails]:
    """Finds target files under a folder, keyed by path relative to the folder."""
    found_files: Dict[str, FileDetails] = {}
    paths: List[Path] = []

    for target_file in target_files:
        paths.extend(current_folder.rglob(target_file))

    for path in paths:
        if denylist_pathnames and any(x in str(path) for x in denylist_pathnames):
            continue

        with open(str(path), "r") as file:
            file_name = str(path.relative_to(current_folder))

            found_files[file_name] = FileDetails(
                name=file_name, path=path, contents=file.read()
            )

    return found_files
