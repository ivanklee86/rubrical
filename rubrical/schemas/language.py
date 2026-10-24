from dataclasses import dataclass

from rubrical.enum import VersionDialect


@dataclass
class LanguageDeclaration:
    # The declared version range, e.g. `>=3.7`.
    version: str
    # The declaration as shown in reports, e.g. `requires-python >=3.7`.
    raw_constraint: str
    dialect: VersionDialect
