from dataclasses import dataclass
from typing import List

from rubrical.enum import DependencySpecifications


@dataclass
class Specification:
    version: str
    specifier: DependencySpecifications


@dataclass
class Package:
    name: str
    raw_constraint: str
    version_constraints: List[Specification]
