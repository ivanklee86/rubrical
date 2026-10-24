"""
Reads version manager files the way the tool that owns each file does.

Each function returns the declared version lines, or an empty list when the file declares nothing.
See `docs/agents/plans/language-version-files.md` for the rules and sources.
"""

import re
from typing import List, Optional

from rubrical.enum import VersionDialect
from rubrical.schemas.language import LanguageDeclaration

NVMRC_COMMENT = re.compile(r"#.*")


def _lines(contents: str) -> List[str]:
    stripped = (line.strip() for line in contents.splitlines())
    return [line for line in stripped if line and not line.startswith("#")]


def python_version(contents: str) -> List[str]:
    # uv parses the whole line; pyenv's first-word rule only differs for trailing text, which uv rejects.
    return _lines(contents)


def go_version(contents: str) -> List[str]:
    # goenv keeps the first word of each line.
    return [line.split()[0] for line in _lines(contents)]


def node_version(contents: str) -> List[str]:
    # nodenv keeps only the first word of the file.
    return contents.split()[:1]


def nvmrc(contents: str) -> List[str]:
    # nvm strips comments anywhere in a line and ignores reserved `key=value` lines.
    stripped = (NVMRC_COMMENT.sub("", line).strip() for line in contents.splitlines())
    versions = [line for line in stripped if line and "=" not in line]

    # nvm rejects more than one version, so they're kept together as one value, which isn't gradeable.
    return [" ".join(versions)] if versions else []


def declaration(
    file_name: str, versions: List[str], dialect: VersionDialect
) -> Optional[LanguageDeclaration]:
    if not versions:
        return None

    return LanguageDeclaration(
        version="\n".join(versions),
        raw_constraint=" ".join([file_name] + [f'"{x}"' for x in versions]),
        dialect=dialect,
    )
